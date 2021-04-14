#!/bin/bash

#===========================
# 1、需先登入各harbor: docker login <HARBOR_URL>
# 2、自行复制 harbor ca至/etc/docker/certs/<HARBOR_URL>/ca.crt
#============================

# 镜像清单档名
lst=/root/harbor17-img.lst
# Harbor 1.7
harbor17_url=harbor17.mydomain
harbor2_url=harbor2.mydomain

local_img=/root/.local_img
# get local images IDs
echo "获取本地镜像清单: ${local_img}"
docker images|grep harbor|awk '{print $1$2" "$3}' > ${local_img}

cat $lst|while read prj app img17 img20;do

    dsk=`df -m /|grep root|awk '{print $4}'`

    # 检查磁盘空间
    if [ $dsk -lt 50000 ];then
        MyMessage="Harbor2 Disk Capacity low"
        echo $MyMessage
        exit 1
    fi

    # check img ID(harbor=img_id, harbor2=img_id2)
    echo "检测local镜像，取得 img_id, img_id2"
    #img_id=`docker images|grep $prj|grep $app|awk '{print $1$2" "$3}'|grep "$prj$app"| awk '{print $2}'|uniq`
    #img_id2=`docker images|grep $prj|grep 'harbor2.xc'|grep $app|awk '{print $1$2" "$3}'|grep "$prj$app"| awk '{print $2}'|uniq`
    img_id=`grep "$prj$app" ${local_img}|awk '{print $2}'|uniq`
    img_id2=`grep "$prj$app" ${local_img}|grep 'harbor2.xc'|awk '{print $2}'|uniq`

    echo "img_id=${img_id}, img_id2=${img_id2}"

    # 检查复制是否完成，跳下一笔
    if [ "$img_id" != "" ] && [ "$img_id2" != "" ];then
        echo "$prj$app 已完成复制"
        continue
    fi
    
    # 检查 img_id，不存在则拉回镜像并取得img_id
    if [ "$img_id" == "" ];then 
        echo "img_id不存在，拉取 harbor 源镜像"
        docker pull -q $img17
        # check pull result
        if [ $? == "0" ];then
            img_id=`docker images|grep $prj|grep $app|awk '{print $1$2" "$3}'|grep "$prj$app"| awk '{print $2}'|uniq`
            echo $img_id
        else
            echo "（错误）$prj$app 不存在"
            echo $img17" not found" >> img-notfound.lst
            #NotifyMM "（错误）$prj$app 不存在"
            continue
        fi
    fi

    # 检查 img_id2，不存在则推送镜像
    if [ "$img_id2" == "" ] && [ "$img_id" != "" ] ;then
        echo "img_id2不存在，推送镜像至harbor2"
        SECONDS=0
        img2="$harbor2_url"${img17#$harbor17_url*}
        docker tag $img_id $img20
        docker push $img20
        ELAPSED="$prj$app 完成复制耗时: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
        #NotifyMM "$ELAPSED"
    fi

    # clear img id from img-lsit
    sed -i '/'$app'/d' $lst


done