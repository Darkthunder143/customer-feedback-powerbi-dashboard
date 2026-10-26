// Create a Power Query parameter named pDataFolder (type: Text) containing an absolute path to the downloaded /data folder.
let
  Source = Csv.Document(File.Contents(pDataFolder & "feedback.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
  Types = Table.TransformColumnTypes(Headers, {{"feedback_id", type text}, {"feedback_date", type date}, {"shop_id", type text}, {"feedback_channel", type text}, {"feedback_type", type text}, {"category", type text}, {"sentiment", type text}, {"csat_score", type number}, {"severity", type text}, {"resolution_status", type text}, {"resolution_hours", type number}, {"product_category", type text}, {"order_channel", type text}, {"feedback_text", type text}}, "en-GB")
in
  Types
