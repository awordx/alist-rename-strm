import time
import sys
from .log_utils import logger
def auto_copy(alist_rename):
    for source_dir, target_dir in zip(alist_rename.source_directory,alist_rename.target_directory):
        names = alist_rename.alist.get_folder_files(source_dir)
        if names is not None:
            logger.info(f'开始执行自动复制')
            logger.info(f'{target_dir}->{source_dir}')
            for name in names:
                alist_rename.alist.copy_file(source_dir, target_dir, name)
                time.sleep(10)
                names = alist_rename.alist.get_folder_files(target_dir+'/'+name)
                if names is not None and names != False:
                    logger.info(f'成功复制：{names}')
                    alist_rename.alist.delete_file(source_dir+'/'+name)
                else:
                    logger.info(f'复制较慢，可能目标网盘没有资源。进行后台复制,待复制完成后需手动刷新,开始退出!')
                    sys.exit()
        else:
            # logger.info(f'❌复制源文件夹：{alist_rename.source_directory} 为空：')
            pass