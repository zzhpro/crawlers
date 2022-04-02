echo `date` START >> /home/data/zhangzhenhao-21/crawlers/log/news.log
source /home/zhangzhenhao-21/miniconda3/etc/profile.d/conda.sh
conda activate crawl
python /home/data/zhangzhenhao-21/crawlers/src/mitcsail.py
echo `date` Done >> /home/data/zhangzhenhao-21/crawlers/log/news.log
