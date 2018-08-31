import  os
import arrow


def isExistPath(path):
    # 此函数用于判断路径是否存在
    # 如果此文件存在 返回True 否则返回False
    if os.path.exists(path):  # 判断路径是否存在
        print(u"目标已存在:", path)  # 如果存在 打印路径已存在,
        return True
    else:
        print(u"目标未找到:", path)  # 如果存在 打印路径已存在,
        return False



def createNewDir():
    #此函数用于在当前目录下生成一个YYYYMMDDHHmmss 格式的文件夹
    #  如果此文件存在 则返回文件夹路径
    createTime = arrow.now().format('YYYYMMDDHHmmss')  # 创建要保存数据的文件夹
    filePath = os.getcwd() + '\\tab\\' + createTime + '\\'  # 拼接文件夹以当天日期命名
    if os.path.exists(filePath):  # 判断路径是否存在
        print(u"目标已存在:", filePath)  # 如果存在 打印路径已存在,
    else:
        os.makedirs(filePath)  # 如果不存在 创建目录
    return filePath


def createDir(path):
    # 此函数用于在当前目录下生成path路径的文件夹
    # 如果此文件存在 则返回文件夹路径

    if os.path.exists(path):  # 判断路径是否存在
        print(u"目标已存在:", path)  # 如果存在 打印路径已存在,
    else:
        os.makedirs(path)  # 如果不存在 创建目录
    return os.path.abspath(path)




if __name__ =='__main__' :
    print('newDir: ',createNewDir())