#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

static int server_socket = 0, client_socket = 0;

int lf_socket_init(char * path)
{
    int t, len;
    struct sockaddr_un local, remote;
    char str[100];

    if ((server_socket = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        perror("server_socket ");
        exit(1);
    }

    local.sun_family = AF_UNIX;
    strcpy(local.sun_path, path);
    unlink(local.sun_path);
    len = strlen(local.sun_path) + sizeof(local.sun_family);
    if (bind(server_socket , (struct sockaddr *)&local, len) == -1) {
        perror("bind");
        exit(1);
    }

    if (listen(server_socket, 5) == -1) {
        perror("listen");
        exit(1);
    }

    printf("Waiting for a connection...\n");
    t = sizeof(remote);
    if ((client_socket = accept4(server_socket , (struct sockaddr *)&remote, &t, SOCK_NONBLOCK)) == -1) {
        perror("accept");
        exit(1);
    }
    printf("Client Socket connected.\n");
}

int lf_receive(char * p_data, int * p_len)
{
    ssize_t len;
    if(!client_socket)
    {
        perror("Client Socket is unitialised");
        return 1;
    }
    
    len = recv(client_socket, p_data, 100, 0); /* Todo handle magic numbers */
    if (len <= 0) 
    {
        *p_len = 0;
        /* We see error codes of -1 when there is no data to be received.
             We still want to keep listening so don't return an error. */
        if (len < -1)
        {
            perror("recv");
            return 1;
        }
    }
    else
    {
        printf("lennn\n");
        *p_len = (int) len;
    }
    return 0;
}

int lf_send(char * p_data, int len)
{
    if(!client_socket)
    {
        perror("Client Socket is unitialised");
        return 1;
    }
    
   if(send(client_socket, p_data, len, 0) < 0)
   {
       perror("send");
       return 1;
    }
    return 0;
}

int lf_close(void)
{
    if(!client_socket)
    {
        close(client_socket);
    }
}

int main(void)
{
    const char * path = "socket.sock";
    char data[101];
    int data_len, ret;
    lf_socket_init((char *) path);
    while(1)
    {
        ret = lf_receive((char *)&data,&data_len);
        if(ret!=0)
        {
            exit(1);
        }
        if(data_len)
        {
            data[data_len] = '\0';
            printf("lf_receive '%s', %d len\n", (char *) &data, data_len);
        }
        sleep(1);
    }
}

