# coding:utf-8
#定义类自动巡检v1
#萝卜橙子西红柿
#该版本巡检函数目前为同步巡检版
#版本v1，下一步计划优化SWS的提取
#后续计划添加异步巡检函数

from netmiko import ConnectHandler
import time
import os
import pandas as pd
import ipdb
from  datetime import datetime

os.environ["NET_TEXTFSM"] = r"C:\xxxx\00_cus-templates"
def get_output_filename():
      pwd = os.getcwd()
      path = pwd+'\Test_Ins'+datetime.now().strftime('%Y%m%d')
      if not os.path.exists(path):
            os.mkdir(path)
      filename = path+r'\Test_Ins_output_'+datetime.now().strftime(('%Y%m%d'))+'.xlsx'
      return (filename)

SWS = [{'device_type':'huawei',
      'host':'test_sw1',
      'ip':'10.1.1.1',
      'port':22,
      'username':'admin',
      'password':'xxxxxxxx'},
       {'device_type':'huawei',
      'host':'test_sw2',
      'ip':'10.1.1.2',
      'port':22,
      'username':'admin',
      'password':'xxxxxxxx'}
       ]

cmds = {'display version':'version_info',
        'display device':'device_info',
        'display cpu-usage':'cpu_info'}

'''定义自动化巡检交换机的一个类'''
class Magic_Ins_SW(object):
      def __init__(self,sws:dict,cmds:dict):
            self.sws = sws
            self.cmds = cmds
            self.df_list=[]
      def get_ins_item(self):
            names = self.__dict__
            for cmd,dsth in cmds.items():
                  names[dsth]=[]
                  self.df_list.append(names[dsth])
            return(self.df_list)
      '''巡检后更新df_list'''
      def ssh_sync_ins_sw(self):
            for sw in self.sws:
                  connect=ConnectHandler(**sw)
                  for cmd,dsth in self.cmds.items():
                        ins_output = connect.send_command(cmd,use_textfsm=True)
                        df1=pd.DataFrame(columns=['Hostname'],data=[list(sw.values())[1]]*len(ins_output))
                        df2=pd.DataFrame(columns=['Host_IP'],data=[list(sw.values())[2]]*len(ins_output))
                        df=pd.concat([df1,df2,pd.DataFrame(ins_output)],axis=1)
                        for i in range(len(cmds)):
                              if cmd == list(cmds.keys())[i]:
                                    self.df_list[i].append(df)
            for i in range(len(self.df_list)):
                  self.df_list[i]=pd.concat(self.df_list[i],axis=0,ignore_index=True)
            return(self.df_list)
      '''巡检到这里，准备输出一个excel'''
      def output_excel(self,df_final:list,filename):
            sheetname=[]
            for cmd,dsth in self.cmds.items():
                  sheetname.append(dsth)
            with pd.ExcelWriter(filename) as writer:
                  for i in range(len(sheetname)):
                        df_final[i].to_excel(writer,sheet_name=sheetname[i],index=False)

if __name__ == '__main__':
      start_time = time.perf_counter()
      path=get_output_filename()                #获取目标文件生成信息
      Inspection =Magic_Ins_SW(SWS,cmds)        #初始化建立巡检任务
      print(Inspection.get_ins_item())          #生成巡检项目的容器（嵌套空列表）
      df_list = Inspection.ssh_sync_ins_sw()         #执行巡检动作，并生成装载了各项巡检动作输出的dataframe的容器（列表）
      Inspection.output_excel(df_list,path)     #输出excel文件
      end_time = time.perf_counter()-start_time
      print(f'总共耗时共{round(end_time,2)}秒')

#ipdb.set_trace()
