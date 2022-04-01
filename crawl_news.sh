source /home/zhangzhenhao-21/miniconda3/etc/profile.d/conda.sh
conda activate crawl
cd /home/data/zhangzhenhao-21/crawlers
python src/mitcsail.py
echo `date` Done >> log/news.log
