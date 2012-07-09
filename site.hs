#!/usr/bin/runhaskell
{-# LANGUAGE OverloadedStrings #-}
import Control.Applicative
import Control.Arrow ((>>>), (>>^), (^>>), arr)
import Data.List (isSuffixOf, intercalate, sortBy)
import Data.Ord (comparing)
import Data.Maybe (catMaybes)
import Data.Monoid
import Data.Time.Clock (UTCTime)
import Data.Time.Format (parseTime, formatTime)
import Text.Pandoc (Block(..), topDown, writerHtml5, writeHtmlString,
                    readMarkdown, defaultParserState)
import Text.Parsec (alphaNum, anyChar, char, manyTill,
                    parse, option, string, try)
import Text.Parsec.String (Parser)
import System.Locale (defaultTimeLocale)

import qualified Data.Map as M
import qualified Data.Set as S

import Hakyll hiding (pageCompiler, readPage, recentFirst)

import Debug.Trace
traces x = trace (show x) x

{- Example metadata:

    - title: The very first character in a document must be '-'.
    - author-name: Each field begins on a new line with a '-', followed
      by an identifier name and a colon. Everything after that, up till the
      next element, is the value.
    - blah: Contiguous lines,

    and indents, are recommended but optional.
    - end: The metadata section must be terminated by a triple-dash:

    ---

-}

ident = (:) <$> alphaNum <*> many (alphaNum <|> char '-')
metadataField = (,) <$> (char ' ' *> ident <* char ':')
                    <*> (trim <$> manyTill anyChar (try $ string "\n-"))
metadata = char '-' *> manyTill metadataField (string "--")

page :: Parser ([(String, String)], String)
page = do
    meta <- option [] metadata
    body <- many anyChar
    let meta' = ("characters", show $ length body) : meta
    return (meta', body)

readPage :: String -> Page String
readPage = either (error . show) mkPage . parse page "page"
  where mkPage (metadata, body) = Page (M.fromList metadata) body

reduceHeaders (Header n xs) = Header (n+2) xs
reduceHeaders x = x

atomDateFmt = "%Y-%m-%dT%H:%m:%SZ"
humanDateFmt = "%B %e, %Y"

humanizeDate = maybe "" fmt' . parseTime defaultTimeLocale atomDateFmt
  where
    fmt' :: UTCTime -> String
    fmt' = formatTime defaultTimeLocale humanDateFmt

dropIndexHtml url =
    if "index.html" `isSuffixOf` url
        then take (length url - 10) url
        else url

pageCompiler = getResourceString
        >>> readPage
        ^>> changeField "published" normDate
        ^>> changeField "updated" normDate
        ^>> addDefaultFields
        >>> changeField "url" dropIndexHtml
        ^>> renderModificationTime "modified" atomDateFmt
        -- >>> copyField "modified" "updated"
        >>> renderField "published" "pubHuman" humanizeDate
        ^>> renderField "updated" "updHuman" humanizeDate
        ^>> pageReadPandoc
        >>^ fmap (writePandocWith writerOpts . topDown reduceHeaders)
  where
    writerOpts = defaultHakyllWriterOptions { writerHtml5 = True }
    normDate d = if "Z" `isSuffixOf` d then d else d ++ "T00:00:00Z"

recentFirst = reverse . sortBy (comparing (getField "published"))

expandPromoted = map (mkPage . words) . lines . pageBody where
  mkPage (baseurl : title) =
    fromMap . M.fromList $ [("url", '/' : baseurl), ("title", unwords title)]

main :: IO ()
main = do
  let opts = defaultHakyllConfiguration { deployCommand =
        "s3cmd sync --delete-removed _site/ s3://strobe.cc && " ++
        "s3cmd sync --delete-removed _site/ s3://www.strobe.cc" }

  hakyllWith opts $ do
    match "images/*" $ do
        route   idRoute
        compile copyFileCompiler

    match "favicon.ico" $ do
        route   idRoute
        compile copyFileCompiler

    match "css/*" $ do
        route   idRoute
        compile compressCssCompiler

    match "promoted.txt" $ do
        route   idRoute
        compile readPageCompiler

    match "templates/*" $ compile templateCompiler

    let applyBaseTemplate =
            setFieldPageList (take 5 . expandPromoted . head)
                "templates/promolist_item.html" "promolist"
                "promoted.txt"
            >>> applyTemplateCompiler "templates/base.html"

        -- Because the built-in syntax lacks so much as an 'ifdef' operator,
        -- we hardcode this template as a whole.
        applySummaryTemplate page =
            setField "summary" (fmt $ getField "summary" page) page
          where
            fmt "" = ""
            fmt summary =
                let html = writeHtmlString defaultHakyllWriterOptions
                         $ readMarkdown defaultParserState summary
                in "<div class=\"summary\">" ++ html ++ "</div>"

        setByline page = setField "byline" byline page
          where
            byline = intercalate " · " . catMaybes $ infos
            infos = [ fmap ("Published: " ++) $ get "pubHuman"
                    , fmap ("Updated: " ++) $ get "updHuman"
                    , fmap (++ " characters") $ get"characters"
                    ]
            get k = maybe Nothing nonempty $ getFieldMaybe k page
            nonempty "" = Nothing
            nonempty x = Just x

        applyAtomTemplate page tmpl =
            let desc = pageBody $ applyTemplateWith (const "") tmpl page
            in  setField "description" desc page

        compileArticle = compile $ pageCompiler
            >>> require "templates/article_atom.html" applyAtomTemplate
            >>> setByline
            ^>> applySummaryTemplate
            ^>> applyTemplateCompiler "templates/article.html"
            >>> applyBaseTemplate
            >>> relativizeUrlsCompiler

    match (regex "(articles|drafts|pages)/.*[.](md|rst)") $ do
        route   $ gsubRoute "articles/" (const "") `composeRoutes`
                  gsubRoute "drafts/" (const "") `composeRoutes`
                  gsubRoute "pages/" (const "") `composeRoutes`
                  gsubRoute ".md" (const "/index.html") `composeRoutes`
                  gsubRoute ".rst" (const "/index.html")
        compileArticle

    match (regex "(articles|drafts|pages)/.*") $ do
        route   $ gsubRoute "articles/" (const "")
        route   $ gsubRoute "drafts/" (const "")
        route   $ gsubRoute "pages/" (const "")
        compile copyFileCompiler

    let compileIndex lim dir = constA mempty
            >>> setField "title" "strobe.cc"
            ^>> setFieldPageList (lim . recentFirst)
                    "templates/article_item.html" "articles"
                    (regex (dir ++ "/.*[.](md|rst)"))
            >>> applyTemplateCompiler "templates/home.html"
            >>> applyBaseTemplate
            >>^ fmap (relativizeUrls ".")

    let feedConfig = FeedConfiguration "strobe.cc" ""
                                       "Steven Robertson" "http://strobe.cc"
    match "feeds/content.xml" $ route idRoute
    create "feeds/content.xml" $ requireAll_ (regex "articles/.*[.](md|rst)")
        >>> recentFirst
        ^>> renderAtom feedConfig

    match "index.html" $ route idRoute
    create "index.html" $ compileIndex id "articles"

    match "drafts/index.html" $ route idRoute
    create "drafts/index.html" $ compileIndex id "drafts"
