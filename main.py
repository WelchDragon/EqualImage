import os
import threading
from queue import Queue


from PIL import Image, ImageChops

import magic

class diff_image(threading.Thread):  # класс по сравнению картинок.
    """Потоковый обработчик"""

    def __init__(self, queue):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        """Запуск потока"""
        while True:
            # Получаем пару путей из очереди
            files = self.queue.get()
            # Делим и сравниваем
            self.difference_images(files.split(':')[0], files.split(':')[1])
            # Отправляем сигнал о том, что задача завершена
            self.queue.task_done()

    def difference_images(self, img1, img2):
        print(magic.from_file(img1, mime=True))
        if img1[-3:] !='jpg' or img1[-3:] !='JPG' or img2[-3:] !='jpg' or img2!= 'JGP':
            return
        image_1 = Image.open(img1)
        image_2 = Image.open(img2)

        size = [400, 300]  # размер в пикселях
        image_1.thumbnail(size)  # уменьшаем первое изображение
        image_2.thumbnail(size)  # уменьшаем второе изображение

        result = ImageChops.difference(image_1, image_2).getbbox()
        if result == None:
            print(img1, img2, 'matches')
            image_1.show()
            image_2.show()
        return


def main(path):
    imgs = os.listdir(path)  # Получаем список картинок
    queue = Queue()

    # Запускаем поток и очередь
    for i in range(14):  # 4 - кол-во одновременных потоков
        t = diff_image(queue)
        t.setDaemon(True)
        t.start()

        # Даем очереди нужные пары файлов для проверки
    check_file = 0
    current_file = 0

    while check_file < len(imgs):
        if current_file == check_file:
            current_file += 1
            continue
        if current_file!=len(imgs):
            queue.put(path + imgs[current_file] + ':' + path + imgs[check_file])
            current_file += 1
        if current_file == len(imgs):
            check_file += 1
            current_file = check_file

            # Ждем завершения работы очереди
    queue.join()


if __name__ == "__main__":
    path = '../../Pictures/фотки/101MSDCF/'
    #path = './image/'
    main(path)
