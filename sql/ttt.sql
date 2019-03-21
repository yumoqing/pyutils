create or replace view view_tran_history1 as
select PortfolioID,SECURITYID
,max(TradeAmount_0) TradeAmount_0
,max(TradeAmount_1) TradeAmount_1
,max(TradeAmount_2) TradeAmount_2
,max(TradeAmount_3) TradeAmount_3
,max(TradeAmount_4) TradeAmount_4
,max(TradeAmount_5) TradeAmount_5
,max(TradeAmount_6) TradeAmount_6
,max(TradeAmount_7) TradeAmount_7
,max(TradeAmount_8) TradeAmount_8
,max(TradeAmount_9) TradeAmount_9
,max(TradeAmount_10) TradeAmount_10
,max(TradePrice_0) TradePrice_0
,max(TradePrice_1) TradePrice_1
,max(TradePrice_2) TradePrice_2
,max(TradePrice_3) TradePrice_3
,max(TradePrice_4) TradePrice_4
,max(TradePrice_5) TradePrice_5
,max(TradePrice_6) TradePrice_6
,max(TradePrice_7) TradePrice_7
,max(TradePrice_8) TradePrice_8
,max(TradePrice_9) TradePrice_9
,max(TradePrice_10) TradePrice_10 from 
(select PortfolioID,SECURITYID,case when TradeBusinessType is null then TradeAmount
	else 0 end as TradeAmount_0  -- None
,case when trim(TradeBusinessType) = trim('02        ') then TradeAmount
	else 0 end as TradeAmount_1  -- 02        
,case when trim(TradeBusinessType) = trim('07        ') then TradeAmount
	else 0 end as TradeAmount_2  -- 07        
,case when trim(TradeBusinessType) = trim('3         ') then TradeAmount
	else 0 end as TradeAmount_3  -- 3         
,case when trim(TradeBusinessType) = trim('05        ') then TradeAmount
	else 0 end as TradeAmount_4  -- 05        
,case when TradeType is null then TradeAmount
	else 0 end as TradeAmount_5  -- None
,case when trim(TradeType) = trim('到期    ') then TradeAmount
	else 0 end as TradeAmount_6  -- 到期    
,case when trim(TradeType) = trim('首期    ') then TradeAmount
	else 0 end as TradeAmount_7  -- 首期    
,case when trim(TradeType) = trim('01        ') then TradeAmount
	else 0 end as TradeAmount_8  -- 01        
,case when trim(TradeType) = trim('02        ') then TradeAmount
	else 0 end as TradeAmount_9  -- 02        
,case when trim(TradeType) = trim('12        ') then TradeAmount
	else 0 end as TradeAmount_10  -- 12        
,case when TradeBusinessType is null then TradePrice
	else 0 end as TradePrice_0  -- None
,case when trim(TradeBusinessType) = trim('02        ') then TradePrice
	else 0 end as TradePrice_1  -- 02        
,case when trim(TradeBusinessType) = trim('07        ') then TradePrice
	else 0 end as TradePrice_2  -- 07        
,case when trim(TradeBusinessType) = trim('3         ') then TradePrice
	else 0 end as TradePrice_3  -- 3         
,case when trim(TradeBusinessType) = trim('05        ') then TradePrice
	else 0 end as TradePrice_4  -- 05        
,case when TradeType is null then TradePrice
	else 0 end as TradePrice_5  -- None
,case when trim(TradeType) = trim('到期    ') then TradePrice
	else 0 end as TradePrice_6  -- 到期    
,case when trim(TradeType) = trim('首期    ') then TradePrice
	else 0 end as TradePrice_7  -- 首期    
,case when trim(TradeType) = trim('01        ') then TradePrice
	else 0 end as TradePrice_8  -- 01        
,case when trim(TradeType) = trim('02        ') then TradePrice
	else 0 end as TradePrice_9  -- 02        
,case when trim(TradeType) = trim('12        ') then TradePrice
	else 0 end as TradePrice_10  -- 12        

from RPT_Tran_History)
group by PortfolioID,SECURITYID
