{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}

import GHC.Generics
import Data.Aeson
import Data.Text	
import qualified Data.Text.IO as TextIO
import Data.Text.Lazy (toStrict)
import Data.Text.Lazy.Encoding


data MyMsg = MyMsg {
  eventType :: Text
, text :: Text
} deriving (Generic, Show)
instance ToJSON MyMsg
instance FromJSON MyMsg

main :: IO ()
main = do
    TextIO.putStrLn(toStrict . decodeUtf8 . encode $ MyMsg {eventType = "timer update", text = "xxx"})
