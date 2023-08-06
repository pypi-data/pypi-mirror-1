teststr = '''
SELECT atc.column_name,
CASE atc.nullable WHEN 'Y' THEN 'NULL' ELSE 'NOT NULL' END "Null?",
atc.data_type ||
CASE atc.data_type WHEN 'DATE' THEN ''
ELSE '(' ||
CASE atc.data_type WHEN 'NUMBER' THEN TO_CHAR(atc.data_precision) ||
CASE atc.data_scale WHEN 0 THEN ''
ELSE ',' || TO_CHAR(atc.data_scale) END
ELSE TO_CHAR(atc.data_length) END 
END ||
CASE atc.data_type WHEN 'DATE' THEN '' ELSE ')' END
data_type
FROM all_tab_columns atc
WHERE atc.table_name = :object_name
AND      atc.owner = :owner
ORDER BY atc.column_id;'''