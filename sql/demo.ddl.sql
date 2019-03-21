


drop table songs;
CREATE TABLE songs
(

  songid VARCHAR(32) ,
  prepath VARCHAR(2000) ,
  filename VARCHAR(2000) ,
  singer VARCHAR(500) ,
  songname VARCHAR(500) ,
  lang VARCHAR(100) ,
  vformat VARCHAR(100) ,
  pinyin VARCHAR(100) ,
  music_track int 


,primary key(songid)


)engine=innodb default charset=utf8 ;
COMMENT ON TABLE songs IS '歌库';

COMMENT ON COLUMN songs.songid is '歌曲编号';

COMMENT ON COLUMN songs.prepath is '盘编号';

COMMENT ON COLUMN songs.filename is '文件名';

COMMENT ON COLUMN songs.singer is '歌手';

COMMENT ON COLUMN songs.songname is '歌名';

COMMENT ON COLUMN songs.lang is '语言';

COMMENT ON COLUMN songs.vformat is '视频格式';

COMMENT ON COLUMN songs.pinyin is '歌曲拼音';

COMMENT ON COLUMN songs.music_track is '伴奏音轨';


