{-# LANGUAGE OverloadedStrings #-}
module Main where
import Data.Char (isPunctuation, isSpace)
import Data.Monoid (mappend)
import Data.Text (Text)
import Control.Exception (finally)
import Control.Monad (forM_, forever)
import Control.Concurrent (MVar, newMVar, modifyMVar_, modifyMVar, readMVar)
import qualified Data.Text as T
import qualified Data.Text.IO as T
import qualified Network.WebSockets as WS

type Client = (Text, WS.Connection)
type ServerState = [Client]

newServerState :: ServerState
newServerState = []

numClients :: ServerState -> Int
numClients = length

meow :: WS.Connection -> IO ()
meow conn = forever $ do
    msg <- WS.receiveData conn
    T.putStrLn ("received " `T.append` msg)
    WS.sendTextData conn $ msg `T.append` ", meow"

application state pending = do
    conn <- WS.acceptRequest pending
    WS.forkPingThread conn 10
    putStrLn "a user connected ..."
    WS.sendTextData conn ("Hi" :: Text)
    meow conn

main :: IO ()
main = do
    state <- newMVar newServerState
    WS.runServer "127.0.0.1" 9160 $ application state
