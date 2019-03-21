SELECT tablename = d.name
       ,tablenote = Isnull(f.VALUE,'')
       ,fieldid = a.colorder
       ,name = a.name
       ,prikey = CASE 
               WHEN EXISTS (SELECT 1
                            FROM   sysobjects
                            WHERE  xtype = 'PK'
                                   AND name IN (SELECT name
                                                FROM   sysindexes
                                                WHERE  indid IN (SELECT indid
                                                                 FROM   sysindexkeys
                                                                 WHERE  id = a.id
                                                                        AND colid = a.colid))) THEN '1'
               ELSE '0'
             END
       ,type = b.name
       ,length = Columnproperty(a.id,a.name,'PRECISION')
       ,dec = Isnull(Columnproperty(a.id,a.name,'Scale'),0)
       ,nullable = CASE 
                WHEN a.isnullable = 1 THEN 'yes'
                ELSE 'no'
              END
       ,vdefault = Isnull(e.TEXT,'')
       ,comments = Isnull(g.[value],'')
FROM     syscolumns a
         LEFT JOIN systypes b
           ON a.xusertype = b.xusertype
         INNER JOIN sysobjects d
           ON (a.id = d.id)
              AND (d.xtype = 'U')
              AND (d.name <> 'dtproperties') 
          INNER JOIN  sys.all_objects c
            ON d.id=c.object_id 
                AND  schema_name(schema_id)='dbo'
         LEFT JOIN syscomments e
           ON a.cdefault = e.id
         LEFT JOIN sys.extended_properties g
           ON (a.id = g.major_id)
              AND (a.colid = g.minor_id)
         LEFT JOIN sys.extended_properties f
           ON (d.id = f.major_id)
              AND (f.minor_id = 0)
--where d.name='bond_value'         --如果只查询指定表,加上此条件
ORDER BY a.id
         ,a.colorder