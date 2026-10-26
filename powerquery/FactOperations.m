// Create a Power Query parameter named pDataFolder (type: Text) containing an absolute path to the downloaded /data folder.
let
  Source = Csv.Document(File.Contents(Text.TrimEnd(pDataFolder, {"/", "\"}) & "/" & "operations.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  Types = Table.TransformColumnTypes(Headers, {{"shop_id", type text}, {"month_start", type date}, {"transactions", Int64.Type}, {"avg_queue_minutes", type number}, {"stock_availability_pct", type number}, {"avg_basket_gbp", type number}, {"staffing_hours", type number}, {"on_time_online_orders_pct", type number}}, "en-GB")
in
  Types
