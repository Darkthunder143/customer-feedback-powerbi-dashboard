let
  First = List.Min(DimMonth[MonthStart]),
  Last = Date.EndOfMonth(List.Max(DimMonth[MonthStart])),
  Dates = List.Dates(First, Duration.Days(Last - First) + 1, #duration(1,0,0,0)),
  Base = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
  Types = Table.TransformColumnTypes(Base, {{"Date", type date}}),
  Month = Table.AddColumn(Types, "MonthStart", each Date.StartOfMonth([Date]), type date),
  Labels = Table.AddColumn(Month, "YearMonth", each Date.ToText([Date], "yyyy-MM"), type text)
in
  Labels
