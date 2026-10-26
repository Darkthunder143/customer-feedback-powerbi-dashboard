let
  First = List.Min(FactOperations[month_start]),
  Last = List.Max(FactOperations[month_start]),
  Months = List.Generate(() => First, each _ <= Last, each Date.AddMonths(_, 1)),
  Base = Table.FromList(Months, Splitter.SplitByNothing(), {"MonthStart"}),
  Types = Table.TransformColumnTypes(Base, {{"MonthStart", type date}}),
  Labels = Table.AddColumn(Types, "YearMonth", each Date.ToText([MonthStart], "yyyy-MM"), type text),
  Year = Table.AddColumn(Labels, "Year", each Date.Year([MonthStart]), Int64.Type)
in
  Year
