import requests, re, json, sqlite3


class BilibiliUser:
    def __init__(self, name):
        self.set = MyDB(name)
        self.name = name
        self.url1 = 'https://api.bilibili.com/x/relation/stat'
        self.url2 = 'https://api.bilibili.com/x/space/upstat'
        self.params1 = {'jsonp': 'jsonp',
                        'callback': '__jp4'}
        self.params2 = {'jsonp': 'jsonp',
                        'callback': '__jp5'}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Host': 'api.bilibili.com',
            'Referer': 'https://space.bilibili.com/'}


    def create(self):
        # create a database
        table = 'users'
        columns = ['UID', 'Following', 'Follower', 'Like', 'View']
        colomns_type = ['Int', 'Int', 'Int', 'Int', 'Int']
        primary_key = 'PRIMARY KEY ({})'.format(columns[0])
        self.set.cDB(table, columns, colomns_type, primary_key)


    def get(self, head_mid, tail_mid):
        # get data from Internet and pass it to process()
        mid = [str(i) for i in range(int(head_mid), int(tail_mid) + 1)]
        for each in mid:
            self.params1['vmid'] = each
            self.params2['mid'] = each
            html1 = requests.get(self.url1, headers=self.headers, params=self.params1).text.replace('__jp4(', '').replace(')', '')
            html2 = requests.get(self.url2, headers=self.headers, params=self.params2).text.replace('__jp5(', '').replace(')', '')
            data = [json.loads(html1)['data'], json.loads(html2)['data']]
            columns = []
            values = []
            for each in data:
                if each is not None:
                    columns += each.keys()
                    values += each.values()
            if columns != []:
                self.process(columns, values)
        print('Done')


    def process(self, columns, values):
        # data processing and pass new data to class MyDB
        dic = {}
        for i in range(len(columns)):
            dic[columns[i]] = values[i]
        dic['UID'] = dic['mid']
        del dic['mid']
        if 'likes' in dic:
            dic['like'] = dic['likes']
            del dic['likes']
        if 'archive' in dic:
            dic['view'] = dic['archive']['view']
            del dic['archive']
        if 'article' in dic:
            del dic['article']
        del dic['whisper']
        del dic['black']
        self.set.wDB('users', dic.keys(), dic.values())


    def show(self, order=1, limit=''):
        # use some simple command to show data from database
        print('排序由order参数控制：1.UID 2.关注数 3.粉丝数 4.获赞数 5.播放量\n显示个数由limit参数控制.')
        if limit != '':
            limit = " limit " + str(limit)
        choice = [0, 'UID', 'Following', 'Follower', 'Like', 'View']
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        total = man.execute("SELECT count(*) FROM users").fetchall()[0][0]
        print('总数据量：{}'.format(total))
        command1 = "SELECT * from users order by {} desc {}".format(choice[order], limit)
        cursor1 = man.execute(command1)
        for each in cursor1:
            print("UID:{} 关注数:{} 粉丝数:{} 获赞数:{} 播放量:{}".format(each[0], each[1], each[2], each[3], each[4]))
        conn.close()


    def run(self, head_mid=1, tail_mid=1):
        self.get(head_mid, tail_mid)


class MyDB:
    def __init__(self, name):
        self.name = name


    def cDB(self, table='example', columns=["'ex_column'"], colomns_type=['text'], primary_key=''):
        # create a database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        add_time = "date timestamp not null default(datetime('now', 'localtime')),"
        columns_new = ""
        for each in columns:
            columns_new += "{} {},".format(each, colomns_type[columns.index(each)])
        command = "CREATE TABLE {}({} {} {})".format(table, columns_new, add_time, primary_key)
        try:
            man.execute(command)
            conn.commit()
            print('Create TABLE {} successfully'.format(table))
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()


    def wDB(self, table='example', columns=["ex_column"], values=["'ex_data'"]):
        # write values into a database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        columns_new = ""
        for each in columns:
            columns_new += "{},".format(each)
        values_new = ""
        for each in values:
            values_new += "{},".format(each)
        command = "INSERT OR REPLACE INTO '{}'({}) VALUES({})".format(table, columns_new[:-1], values_new[:-1])
        try:
            man.execute(command)
            conn.commit()
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()


    def rDB(self, table='example'):
        # read a database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        #print(man.fetchall())
        command = "SELECT * from '{}'".format(table)
        try:
            for each in man.execute(command):
                print('{}'.format(each))
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()


    def dDB(self, table='example'):
        # delete a database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        command = "DROP TABLE '{}'".format(table)
        try:
            man.execute(command)
            conn.commit()
            print('Delete successfully')
        except sqlite3.OperationalError as reason:
            print(reason)
        conn.close()


if __name__ == "__main__":
    user = BilibiliUser('bilibili_users.db')
    user.create()
    user.run(10000, 10000)
