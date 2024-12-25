import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# Константы
radius = 0.7  # Радиус сферы
N = 25  # Количество разбиений
isGuro = False  # Использовать ли шейдинг Гуро

# Параметры камеры
cameraX, cameraY, cameraZ = 0.0, 0.0, 0.0
cameraAngleHorizontal = 0.0
cameraAngleVertical = 0.0
cameraSpeed = 0.05
lookSpeed = 0.05

# Структура для вершин
class Vertex:
    def __init__(self, x, y, z, nx, ny, nz, intensity):
        self.x = x
        self.y = y
        self.z = z
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.intensity = intensity

vertices = []  # Список всех вершин
indices = []  # Индексы для треугольников

# Функция для вычисления нормали
def calculate_normal(x, y, z):
    length = math.sqrt(x * x + y * y + z * z)
    return x / length, y / length, z / length

def calculate_light_intensity(nx, ny, nz):
    light_dir = np.array([0.0, 0.0, 1.0])  # Направление света
    normalized_light_dir = light_dir / np.linalg.norm(light_dir)  # Нормализация направления света

    # Скалярное произведение нормали и направления света
    dot_product = nx * normalized_light_dir[0] + ny * normalized_light_dir[1] + nz * normalized_light_dir[2]
    return min(max(0.0, dot_product), 1)  # Интенсивность от 0 до 1

# Функция для построения сферы
def build_sphere():
    global vertices, indices
    vertices.clear()
    indices.clear()

    stacks = N  # Количество горизонтальных разбиений
    slices = N  # Количество вертикальных разбиений

    for i in range(stacks + 1):
        phi = math.pi * i / stacks  # Угол по вертикали
        for j in range(slices + 1):
            theta = 2 * math.pi * j / slices  # Угол по горизонтали

            # Вычисление координат вершины
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)

            # Вычисление нормали
            nx, ny, nz = calculate_normal(x, y, z)

            # Вычисление интенсивности света
            intensity = calculate_light_intensity(nx, ny, nz)

            # Добавление вершины
            vertices.append(Vertex(x, y, z, nx, ny, nz, intensity))

    # Создание индексов для треугольников
    for i in range(stacks):
        for j in range(slices):
            first = i * (slices + 1) + j
            second = first + slices + 1

            # Треугольник 1
            indices.append(first)
            indices.append(second)
            indices.append(first + 1)

            # Треугольник 2
            indices.append(first + 1)
            indices.append(second)
            indices.append(second + 1)

# Функция для рендеринга сферы
def render_sphere():
    glBegin(GL_TRIANGLES)
    if isGuro:
        for i in range(0, len(indices), 3):
            for j in range(3):
                v = vertices[indices[i + j]]
                glColor3f(v.intensity, v.intensity, v.intensity)  # Установка цвета
                glNormal3f(v.nx, v.ny, v.nz)  # Установка нормали
                glVertex3f(v.x, v.y, v.z)  # Установка координат
    else:
        for i in range(0, len(indices), 3):
            v0 = vertices[indices[i]]
            glColor3f(v0.intensity, v0.intensity, v0.intensity)  # Установка цвета для первого вершинного треугольника
            for j in range(3):
                v = vertices[indices[i + j]]
                glNormal3f(v.nx, v.ny, v.nz)  # Установка нормали
                glVertex3f(v.x, v.y, v.z)  # Установка координат
    glEnd()

# Функция для обновления экрана
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очистка экрана
    glLoadIdentity()  # Сброс матрицы
    gluLookAt(cameraX, cameraY, cameraZ,
              cameraX + math.sin(cameraAngleHorizontal),
              cameraY + math.tan(cameraAngleVertical),
              cameraZ - math.cos(cameraAngleHorizontal),
              0.0, 1.0, 0.0)  # Установка камеры
    render_sphere()  # Рендеринг сферы
    pygame.display.flip()  # Обновление экрана

# Функция для обработки нажатий клавиш
def handle_keys():
    global cameraX, cameraY, cameraZ, cameraAngleHorizontal, cameraAngleVertical
    keys = pygame.key.get_pressed()
    if keys[K_w]:  # Вперед
        cameraX += cameraSpeed * math.sin(cameraAngleHorizontal)
        cameraZ -= cameraSpeed * math.cos(cameraAngleHorizontal)
    if keys[K_s]:  # Назад
        cameraX -= cameraSpeed * math.sin(cameraAngleHorizontal)
        cameraZ += cameraSpeed * math.cos(cameraAngleHorizontal)
    if keys[K_a]:  # Влево
        cameraX -= cameraSpeed * math.cos(cameraAngleHorizontal)
        cameraZ -= cameraSpeed * math.sin(cameraAngleHorizontal)
    if keys[K_d]:  # Вправо
        cameraX += cameraSpeed * math.cos(cameraAngleHorizontal)
        cameraZ += cameraSpeed * math.sin(cameraAngleHorizontal)
    if keys[K_q]:  # Поворот влево
        cameraAngleHorizontal -= lookSpeed
    if keys[K_e]:  # Поворот вправо
        cameraAngleHorizontal += lookSpeed
    if keys[K_r]:  # Сброс камеры
        cameraX, cameraY, cameraZ = 0.0, 0.0, 0.0
        cameraAngleHorizontal, cameraAngleVertical = 0.0, 0.0

# Основная функция
def main():
    global cameraX, cameraY, cameraZ
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    gluPerspective(60.0, (800 / 600), 0.1, 1000.0)  # Установка перспективы
    glEnable(GL_DEPTH_TEST)  # Включение теста глубины
    glShadeModel(GL_SMOOTH)  # Мягкое затенение
    build_sphere()  # Построение сферы

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        handle_keys()  # Обработка нажатий клавиш
        display()  # Отображение сцены

if __name__ == "__main__":
    main()