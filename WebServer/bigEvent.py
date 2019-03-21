#!/usr/bin/env python
#coding=utf8

import ujson as json
from appPublic.dictObject import DictObject
import pika
from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol,task


class BigEvent(object):
	def __init__(self,host,port,user,passwd):
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self.exchangetype = 'message'
		self.mqtype = 'topic'
		self.queueList = []
		self.credentials = pika.PlainCredentials(self.user, self.passwd)
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host,self.port,'/',self.credentials))

	def __del__(self):
		self.connection.close()
	
	def product(self,evtName,objid,data):
		channel = self.connection.channel()
 
		#定义交换机，设置类型为topic
		channel.exchange_declare(exchange=self.exchangetype, type=self.mqtype)
		d = {
			'objid':objid,
			'data':data,
			'event':evtName,
		}
		message = json.dumps(d)
		#将消息依次发送到交换机，并设定路由键
		channel.basic_publish(exchange=self.exchangetype,routing_key=evtName,body=message)
	
	def consume(self,evtlist,cb):
		@defer.inlineCallbacks
		def read(queue_object,cb):
			ch,method,properties,body = yield queue_object.get()
			id = evt = data = None
			if body:
				try:
					o = DictObject(**json.loads(body))
					id = o.objid
					evt = o.event
					data = o.data
					cb(evt,id,data)
				except Exception as e:
					print("read():Exception=",e,'id=',id,'evt=',evt,'data=',data)
			yield ch.basic_ack(delivery_tag=method.delivery_tag)

		@defer.inlineCallbacks
		def run(connection,evtlist,cb):
			channel = yield connection.channel()
			exchange = yield channel.exchange_declare(exchange=self.exchangetype,type=self.mqtype)
			#生成临时队列，并绑定到交换机上，设置路由键
			result = yield channel.queue_declare(exclusive=True)
			queue_name = result.method.queue
			for routing in evtlist:
				yield channel.queue_bind(exchange=self.exchangetype,queue=queue_name,routing_key=routing)
			yield channel.basic_qos(prefetch_count=1)
			queue_object, consumer_tag = yield channel.basic_consume(queue=queue_name,no_ack=False)
			l = task.LoopingCall(read, queue_object,cb)
			l.start(0.01)


		parameters = pika.ConnectionParameters(self.host, self.port, '/', self.credentials)
		cc = protocol.ClientCreator(reactor, twisted_connection.TwistedProtocolConnection, parameters)
		d = cc.connectTCP(self.host, self.port)
		d.addCallback(lambda protocol: protocol.ready)
		d.addCallback(run,evtlist,cb)
		self.queueList.append([d,evtlist])
		
		
		
