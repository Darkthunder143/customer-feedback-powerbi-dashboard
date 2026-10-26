// Create a Power Query parameter named pDataFolder (type: Text) containing an absolute path to the downloaded /data folder.
let
  Source = Csv.Document(File.Contents(pDataFolder & "shops.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  Types = Table.TransformColumnTypes(Headers, {{"shop_id", type text}, {"shop_label", type text}, {"city", type text}, {"region", type text}, {"format", type text}}, "en-GB")
in
  Types
