// Create a Power Query parameter named pDataFolder (type: Text) containing an absolute path to the downloaded /data folder.
let
  Source = Csv.Document(File.Contents(Text.TrimEnd(pDataFolder, {"/", "\"}) & "/" & "feedback.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, {"resolution_hours"}),
  Types = Table.TransformColumnTypes(Nulls, {{"feedback_id", type text}, {"feedback_date", type date}, {"shop_id", type text}, {"feedback_channel", type text}, {"feedback_type", type text}, {"category", type text}, {"sentiment", type text}, {"csat_score", Int64.Type}, {"severity", type text}, {"resolution_status", type text}, {"resolution_hours", type number}, {"product_category", type text}, {"order_channel", type text}, {"feedback_text", type text}}, "en-GB") ,
  Month = Table.AddColumn(Types, "month_start", each Date.StartOfMonth([feedback_date]), type date)
in
  Month
