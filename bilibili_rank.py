import requests, re, json, sqlite3, datetime, time


class BilibiliRank:
    def __init__(self, name):
        self.set = MyDB(name)
        self.name = name


    def save(self, data):
        table = 'Rank{}'.format(str(datetime.date.today()).replace('-', ''))
        columns = ['mid', 'author', 'title', 'bvid', 'pts']
        columns_type = ['Int', 'text', 'text', 'text', 'Int']
        primary_key = 'PRIMARY KEY ({})'.format(columns[3])
        self.set.cDB(table, columns, columns_type, primary_key)
        dic = {}
        for each in data:
            dic['{}'.format(columns[0])] = each['mid']
            dic[columns[1]] = "'{}'".format(each['author'])
            dic[columns[2]] = "'{}'".format(each['title'])
            dic[columns[3]] = "'{}'".format(each['bvid'])
            dic[columns[4]] = each['pts']
            self.set.wDB(table, dic.keys(), dic.values())
        print('written successfully')


    def run(self):
        worker = GetJson()
        data = worker.runing()
        self.save(data)


class GetJson:
    def __init__(self):
        self.url = 'https://api.bilibili.com/x/web-interface/ranking'
        self.deltext = '__jp14('
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'}
        self.params = {
            'rid': '0',
            'day': '1',
            'type': '1',
            'arc_type': '0',
            'jsonp': 'jsonp',
            'callback': '__jp14'}


    def runing(self):
        text1 = requests.get(self.url, headers=self.headers, params=self.params).text.replace(self.deltext, '')[:-1]
        data = json.loads(text1)['data']['list']
        return data


class MyDB:
    def __init__(self, name):
        self.name = name


    def cDB(self, table='example', columns=['ex_column'], colomns_type=['text'], primary_key=''):
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


    def uDB(self):
        # update data in database throuugh primary key(maybe)
        pass


    def rDB(self, table='example'):
        # read data from database
        conn = sqlite3.connect(self.name)
        man = conn.cursor()
        command = "SELECT * FROM {}".format(table)
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


if __name__ == '__main__':
    rank = BilibiliRank('bilibili_rank.db')
    rank.run()
    time.sleep(1)