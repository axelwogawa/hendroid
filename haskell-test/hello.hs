import Data.Char

shout :: String -> String
shout s = map toUpper s

greet s = "Hello " ++ s

main = do
  putStrLn $ greet . shout $ "foo"
