# 1创建套接字
import socket
import threading


def read(socket_fuwu):
    while True:

        recv_data = socket_fuwu.recv(1024)
        if recv_data:
            socket_fuwu.send(recv_data)


def create_server(port):
    try:
        tcp_socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 服务器端口回收操作（释放端口）
        tcp_socket_host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        # 2绑定端口
        tcp_socket_host.bind(('', port))

        # 3监听  变为被动套接字
        tcp_socket_host.listen(1)  # 128可以监听的最大数量，最大链接数

        # 4等待客户端连接
        socket_fuwu, addr_client = tcp_socket_host.accept()  # accept(new_socket,addr)
        print(socket_fuwu)
        print(addr_client)

        t1 = threading.Thread(target=read, args=(socket_fuwu,))
        t1.start()
    except Exception as e:
        pass

def main():
    for i in range(1, 200):
        t = threading.Thread(target=create_server, args=(i,))
        t.start()

    #6服务套接字关闭
    # socket_fuwu.close()    #服务器一般不关闭   此时服务端口因为需要一直执行所以也不能关闭

if __name__ == '__main__':
    main()