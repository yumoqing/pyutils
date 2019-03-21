select  utc.table_name ,utc.COLUMN_NAME,utc.DATA_TYPE,utc.DATA_LENGTH,utc.data_scale,utc.nullable,ucc.comments
from  user_tab_cols utc left join USER_COL_COMMENTS ucc on utc.table_name = ucc.table_name
where utc.table_name = ${table_name}