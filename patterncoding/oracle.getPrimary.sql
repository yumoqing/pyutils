SELECT
  a.TABLE_NAME,
  a.TABLE_TYPE,
  a.COMMENTS,
  b.column_name
FROM
  USER_TAB_COMMENTS a left join (
			select uc.table_name,col.column_name , uc.constraint_type,case uc.constraint_type when 'P' then '1' else '' end "PrimaryKey"
			from user_tab_columns col left join user_cons_columns ucc on ucc.table_name=col.table_name and ucc.column_name=col.column_name
			left join user_constraints uc on uc.constraint_name = ucc.constraint_name and uc.constraint_type='P'
			where uc.table_name is not null 
) b on a.table_name = b.table_name
where table_type = 'TABLE'
