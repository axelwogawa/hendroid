{-
- Server with websocket connection to UI client and MQTT connection to PI
-}

{-# LANGUAGE DeriveGeneric     #-}
{-# LANGUAGE OverloadedStrings #-}

module Main where
import           Control.Concurrent      (MVar, modifyMVar, modifyMVar_,
                                          newMVar, readMVar)
import           Control.Exception       (finally)
import           Control.Monad           (forM_, forever)
import           Data.Aeson
import           Data.Monoid             (mappend)
import qualified Data.Text               as T
import qualified Data.Text.IO            as TextIO
import           Data.Text.Lazy          (toStrict)
import           Data.Text.Lazy.Encoding (decodeUtf8)
import           GHC.Generics
import qualified Network.WebSockets      as WS
import Network.URI (parseURI)
import qualified Network.MQTT.Client as MQTT
import Debug.Trace (trace)


{- ########################### Websocket to UI client ##########################
- websocket stuff taken from https://jaspervdj.be/websockets/example/server.html
- JSON stuff taken from https://artyom.me/aeson and
-   https://hackage.haskell.org/package/aeson-1.4.7.1/docs/Data-Aeson.html
-}
type Client = (T.Text, WS.Connection)
type ServerState = [Client]

-- defining message format (JSON)
data MyMsg = MyMsg
    { eventType :: T.Text
    , text      :: T.Text
    }
    deriving (Generic, Show)
instance ToJSON MyMsg
instance FromJSON MyMsg

newServerState :: ServerState
newServerState = []

-- communication logic
talk :: WS.Connection -> IO ()
talk conn = forever $ do
    msg <- WS.receiveData conn  -- receiving message
    TextIO.putStrLn ("Received " `T.append` msg)
    -- sending message in standard format
    WS.sendTextData conn $ decodeUtf8 $ encode MyMsg {eventType = "timer update", text = "xxx"}

-- connection handling
application state pending = do
    conn <- WS.acceptRequest pending    -- establishing connection to UI
    WS.forkPingThread conn 10           -- periodic ping
    putStrLn "a user connected ..."
    WS.sendTextData conn ("Hi client, I'm your server!" :: T.Text)
    talk conn                           -- start waiting forever

connectMqtt = do
  let (Just uri) = parseURI "mqtt://localhost"
  mqttClient <- MQTT.connectURI MQTT.mqttConfig{MQTT._msgCB=MQTT.SimpleCallback msgReceived} uri

  print =<< MQTT.subscribe mqttClient [("hello", MQTT.subOptions)] []
  MQTT.waitForClient mqttClient   -- wait for the the client to disconnect

  return mqttClient

  where
    msgReceived _ t m p = print (t,m,p)

fullRequest mqttClient = do
  MQTT.publish mqttClient "fullRequest" "pls give info" False

main :: IO ()
main = do
    state <- newMVar newServerState
    mqttClient <- connectMqtt
    fullRequest mqttClient
    WS.runServer "127.0.0.1" 9160 $ application state

{- ############################ MQTT connection to Pi ##########################
- logic taken from https://jaspervdj.be/websockets/example/server.html
-}
