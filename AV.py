import net_fn
from pyquery import PyQuery as pq
from tqdm import tqdm
import json
from queue import Queue
from threading import  Thread
import time
import m3u8

class AV:

    def __init__(self):
        self.Net = net_fn.Net()
        self.m3u8 = m3u8.M3U8_Downloader(50)
        self.Video_Page_Queue = Queue()
        self.Video_Page_Scapre_Thread_Num = 50 #最大爬蟲線程數
        self.Video_Page_Thread_List = []
        self.Video_Page_Links = []
        self.Loading_Video_Page_Links()#讀取已保存的影片頁面列表
        self.Video_Download_Links = []
        self.Video_Download_Links_Queue = Queue()
        self.Video_Download_Links_Queue_Thread_Num = 50  # 最大爬蟲線程數
        self.Loading_Video_Download_Link() #讀取已保存的影片下載連結
        print('')

    def Download_Video(self,url):
        self.Net.Download(url)
        print("下載完成!!!")

    def Loading_Video_Download_Link(self):
        f = open("Video_Download_Link.txt",'r')
        data = json.load(f)
        f.close()
        self.Video_Download_Links = data

    def Get_Video_Download_Link(self,link):
        header = "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9###accept-encoding: gzip, deflate, br###accept-language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5###cache-control: max-age=0###cookie: ASP.NET_SessionId=c2imwxq4pouvskcujykqbvca; __cfduid=df14915307877e38f662dace4a5d2bb4f1582077741; _ga=GA1.3.817680150.1582077744; _gid=GA1.3.1534557918.1582077744; _gat_gtag_UA_18029176_4=1; _gat_gtag_UA_9475216_1=1###referer: https://www.google.com/###sec-fetch-dest: document###sec-fetch-mode: navigate###sec-fetch-site: cross-site###sec-fetch-user: ?1###upgrade-insecure-requests: 1###user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
        rs = self.Net.Get(url=link,header_string=header)
        data = rs.content.decode()

        #用正規找要得連結
        Get_3gp_Link = self.Net.preg_get_word('file: "(https://.+\.3gp)"',1,data)
        return Get_3gp_Link

    def Thread_Video_Download_Link(self):
        #查看Q是不是空的
        while self.Video_Download_Links_Queue.qsize() != 0:
            #取出Q的值
            link = self.Video_Download_Links_Queue.get()

            download_link = self.Get_Video_Download_Link(link)
            self.Video_Download_Links.append(download_link)
            time.sleep(0.2)
    

    #從每頁把所有影片的連結都保存下來
    def Get_Video_Download_Link_Start_Thread(self):
        # for Page_Link in tqdm(self.Video_Page_Links,desc="分配下載連結任務"):
        #     self.Video_Download_Links_Queue.put(Page_Link)
        for Page_Link in self.Video_Page_Links[0:300]:
            #將所有連結都放到Q裡面
            self.Video_Download_Links_Queue.put(Page_Link)
        for n in range(self.Video_Download_Links_Queue_Thread_Num):#=50
            t = Thread(target=self.Thread_Video_Download_Link)
            t.start()
        print("開始進行獲取影片")
        Total_Mission = self.Video_Download_Links_Queue.qsize() 

        while self.Video_Download_Links_Queue.qsize() != 0:
            print("影片連結獲取進度：{}/{}".format(self.Video_Download_Links_Queue.qsize(), Total_Mission))
            time.sleep(1)
        fp = open("Video_Download_Link.txt","w+")
        fp.write(json.dumps(self.Video_Download_Links))
        fp.close()
        print("工作完成，保存完畢下載連結")




    def Loading_Video_Page_Links(self):
        file_name = "Video_Page_Link.txt"
        f = open(file_name,'r')
        data = f.read()
        f.close()
        self.Video_Page_Links = json.loads(data)



    #抓出總共有幾頁
    def Get_Page_Max_Number(self):
        url = "https://airav.cc/index.aspx?idx=1"
        header = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9###Accept-Encoding: gzip, deflate, br###Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5###Cache-Control: max-age=0###Connection: keep-alive###Cookie: UM_distinctid=1705b875f85cf-0cb729bec7926a-b791b36-1fa400-1705b875f86137; CNZZDATA4000003=cnzz_eid%3D770345665-1582080959-https%253A%252F%252Flink.zhihu.com%252F%26ntime%3D1582080959; Hm_lvt_536e798a6b4ff16f87e8fbebde347f50=1582083564; Hm_lpvt_536e798a6b4ff16f87e8fbebde347f50=1582083961; sid=26724835.422929572.1582083715196.1582083961729###Host: one-piece.cn###If-Modified-Since: Fri, 14 Feb 2020 06:23:45 GMT###If-None-Match: 802e2a4fffe2d51:0###Sec-Fetch-Dest: document###Sec-Fetch-Mode: navigate###Sec-Fetch-Site: none###Sec-Fetch-User: ?1###Upgrade-Insecure-Requests: 1###User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
        rs = self.Net.Get(url=url, header_string=header)
        data = rs.content.decode()
        py_txt = pq(data).find(".nextback")
        Last_Page_Num_Ele = py_txt.eq(len(py_txt) -1 ).html()
        Last_Page_Num = pq(Last_Page_Num_Ele).attr('href').replace("/index.aspx?idx=","")
        return int(Last_Page_Num)


    def Get_Page_Video(self,page_num):
        url = "https://airav.cc/index.aspx?idx="+format(page_num)
        header = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9###Accept-Encoding: gzip, deflate, br###Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5###Cache-Control: max-age=0###Connection: keep-alive###Cookie: UM_distinctid=1705b875f85cf-0cb729bec7926a-b791b36-1fa400-1705b875f86137; CNZZDATA4000003=cnzz_eid%3D770345665-1582080959-https%253A%252F%252Flink.zhihu.com%252F%26ntime%3D1582080959; Hm_lvt_536e798a6b4ff16f87e8fbebde347f50=1582083564; Hm_lpvt_536e798a6b4ff16f87e8fbebde347f50=1582083961; sid=26724835.422929572.1582083715196.1582083961729###Host: one-piece.cn###If-Modified-Since: Fri, 14 Feb 2020 06:23:45 GMT###If-None-Match: 802e2a4fffe2d51:0###Sec-Fetch-Dest: document###Sec-Fetch-Mode: navigate###Sec-Fetch-Site: none###Sec-Fetch-User: ?1###Upgrade-Insecure-Requests: 1###User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
        rs = self.Net.Get(url=url,header_string=header)
        data = rs.content.decode()
        List_Item = pq(data).find('.listItem')

        Video_List = []
        for Video_Item  in List_Item:
            Link = pq(Video_Item).find('.ga_click').attr('href')
            Link = "https://airav.cc/"+Link

            Video_List.append(Link)

        return Video_List
    def Thread_Get_Page_Video(self):
        while self.Video_Page_Queue.qsize() != 0:
            Page_Number = self.Video_Page_Queue.get()
            links = self.Get_Page_Video(Page_Number)
            for link in links:
                self.Video_Page_Links.append(link)

            time.sleep(0.2)

    def Scrape_All_Video_Page_Link(self):
        Page_Max = self.Get_Page_Max_Number()
        All_Links = []
        for n in tqdm(range(1,Page_Max),desc="正在分配爬行連結任務"):
            self.Video_Page_Queue.put(n)

        for n in range(self.Video_Page_Scapre_Thread_Num):
            t = Thread(target=self.Thread_Get_Page_Video)
            t.start()

            self.Video_Page_Thread_List.append(t)

        Total_Mission = self.Video_Page_Queue.qsize()
        while self.Video_Page_Queue.qsize() != 0:
            print("抓取每頁連結爬蟲進度：{}/{}".format(self.Video_Page_Queue.qsize(),Total_Mission))
            time.sleep(1)

        f = open("Video_Page_Link.txt",'w+')
        f.write(json.dumps(self.Video_Page_Links))
        f.close()


if __name__ == "__main__":
    obj = AV()
    obj.Get_Video_Download_Link(obj.Video_Page_Links[1])
    # obj.Get_Video_Download_Link_Start_Thread()
    # print(obj.Video_Download_Links)
    #obj.Download_Video(obj.Video_Download_Links[0])
    # obj.Scrape_All_Video_Page_Link()