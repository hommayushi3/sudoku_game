import sys, pygame, random
from copy import deepcopy
pygame.init()

size = width, height = 600, 500
white = 255, 255, 255
gray = 100, 100, 100
black = 0, 0, 0
num_offset = 535

screen = pygame.display.set_mode(size)

tile_dim = 54
screen.fill(white)
dig_images = []
dig_images_rects = []

for i in range(10):
	pic_name = str(i) + ".jpg"
	dig_images.append(pygame.image.load(pic_name).convert())
	dig_images_rects.append(dig_images[-1].get_rect())
	dig_images_rects[i].center = (num_offset, 7 + tile_dim * (i - 0.5) )
	screen.blit(dig_images[i], dig_images_rects[i])

eraser = pygame.image.load("erase.jpg").convert()
eraser_rect = eraser.get_rect()
eraser_rect.center = (573, 22)
screen.blit(eraser, eraser_rect)

for col in range(10):
	width = 1
	if col % 3 == 0:
		width = 3
	pygame.draw.line(screen, black, (7 + tile_dim * col, 7), 
		(7 + tile_dim * col, 493), width)
	pygame.draw.line(screen, black, (7, 7 + tile_dim * col),
		(493, 7 + tile_dim * col), width)

def switch_cols(grid, col1, col2):
	temp_col = deepcopy(grid[col1])
	grid[col1] = deepcopy(grid[col2])
	grid[col2] = temp_col
	return grid

def switch_col_group(grid, colg1, colg2):
	for i in range(3):
		grid = switch_cols(grid, 3 * colg1 + i, 3 * colg2 + i)
	return grid

def switch_rows(grid, row1, row2):
	temp_grid = [[grid[i][j] if j != row1 else grid[i][row2] for j in range(9)] for i in range(9)]
	return [[temp_grid[i][j] if j != row2 else grid[i][row1] for j in range(9)] for i in range(9)]

def switch_row_group(grid, rowg1, rowg2):
	for i in range(3):
		grid = switch_rows(grid, 3 * rowg1 + i, 3 * rowg2 + i)
	return grid

def rotate_grid(grid):
	return [[grid[i][8 - j] for i in range(9)] for j in range(9)]

def flip_grid(grid):
	return [[grid[i][j] for i in range(9)] for j in range(9)]

def randomize_grid(grid):
	for i in range(random.randint(6, 15)):
		col1 = random.randint(0, 8)
		col2 = 3 * int(col1 / 3) + (col1 + random.randint(1, 2)) % 3 
		grid = switch_cols(grid, col1, col2)

	for i in range(random.randint(6, 15)):
		row1 = random.randint(0, 8)
		row2 = 3 * int(row1 / 3) + (row1 + random.randint(1, 2)) % 3 
		grid = switch_rows(grid, row1, row2)

	for i in range(random.randint(0, 3)):
		colg1 = random.randint(0, 2)
		colg2 = (colg1 + random.randint(1, 2)) % 3
		grid = switch_col_group(grid, colg1, colg2)

	for i in range(random.randint(0, 3)):
		rowg1 = random.randint(0, 2)
		rowg2 = (rowg1 + random.randint(1, 2)) % 3
		grid = switch_row_group(grid, rowg1, rowg2)

	for i in range(random.randint(0, 3)):
		grid = rotate_grid(grid)

	for i in range(random.randint(0, 1)):
		grid = flip_grid(grid)

	return grid

perm = {i: 0 for i in range(1, 10)}
unused = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for key in perm:
	index = random.randint(0, len(unused) - 1)
	perm[key] = unused[index]
	del unused[index]

solution_grid = [[ perm[(i * 3 + i / 3 + j) % 9 + 1] for i in range(9)] for j in range(9)]
solution_grid = randomize_grid(solution_grid)

rows = [{i: 0 for i in range(1, 10)} for j in range(9)]
columns = [{i: 0 for i in range(1, 10)} for j in range(9)]
blocks = [{i: 0 for i in range(1, 10)} for j in range(9)]

original_list = []
filled_grid = [[0 for i in range(9)] for j in range(9)]

blocks_count = [0 for i in range(9)]
for row in range(9):
	cols = []
	for n in range(int(2.875 + 1.25 * random.random())):	
		col = random.randint(0, 8)
		while col in cols:
			col = random.randint(0, 8)
		cols.append(col)
		
		original_list.append((row, col))
		num = solution_grid[row][col]
		rows[row][num] += 1
		columns[col][num] += 1
		blocks[int(row / 3) + 3 * int(col / 3)][num] += 1
		filled_grid[row][col] = num

		blocks_count[int(row / 3) + 3 * int(col / 3)] += 1

		image = dig_images[num]
		image_rect = image.get_rect()
		image_rect.center = (34 + tile_dim * row, 34 + tile_dim * col) 
		screen.blit(image, image_rect)

for i in range(9):
	count = blocks_count[i]
	if count == 0:
		seed = random.randint(0, 8)
		row = int(i % 3) * 3 + seed % 3
		col = int(i / 3) * 3 + seed / 3

		original_list.append((row, col))
		num = solution_grid[row][col]
		rows[row][num] += 1
		columns[col][num] += 1
		blocks[int(row / 3) + 3 * int(col / 3)][num] += 1
		filled_grid[row][col] = num

		image = dig_images[num]
		image_rect = image.get_rect()
		image_rect.center = (34 + tile_dim * row, 34 + tile_dim * col) 
		screen.blit(image, image_rect)


pygame.display.flip()

mouse_down_tile = None
cursor_mode = - 1

def condition_satisfied(container):
	for con in container:
		for key in con:
			if con[key] != 1:
				return False
 	return True

def check_finished(rows, columns, blocks):
	return condition_satisfied(rows) and condition_satisfied(columns) and condition_satisfied(blocks)

pygame.event.set_blocked([pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.KEYUP, pygame.JOYAXISMOTION, 
	pygame.JOYBALLMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN, pygame.VIDEORESIZE,
	pygame.VIDEOEXPOSE, pygame.USEREVENT, pygame.ACTIVEEVENT])
while True:
	pygame.event.wait
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = event.pos
			if mouse_x >= 7 and mouse_y >= 7 and mouse_y < 493:
				tile_x, tile_y = int((mouse_x - 7)/ tile_dim), int((mouse_y - 7)/ tile_dim)
				if mouse_x < 493 and (tile_x, tile_y) not in original_list and cursor_mode != -1:
					image = dig_images[cursor_mode]
					image_rect = image.get_rect()
					image_rect.center = (34 + tile_dim * tile_x, 34 + tile_dim * tile_y) 
					screen.blit(image, image_rect)
					pygame.display.update(image_rect)

					if cursor_mode == 0:
						num = filled_grid[tile_x][tile_y]
						rows[tile_x][num] -= 1
						columns[tile_y][num] -= 1
						blocks[int(tile_x / 3) + 3 * int(tile_y / 3)][num] -= 1
						filled_grid[tile_x][tile_y] = 0

					elif filled_grid[tile_x][tile_y] == 0:
						rows[tile_x][cursor_mode] += 1
						columns[tile_y][cursor_mode] += 1
						blocks[int(tile_x / 3) + 3 * int(tile_y / 3)][cursor_mode] += 1
						filled_grid[tile_x][tile_y] = cursor_mode

					elif filled_grid[tile_x][tile_y] != cursor_mode:
						num = filled_grid[tile_x][tile_y]
						rows[tile_x][num] -= 1
						columns[tile_y][num] -= 1
						blocks[int(tile_x / 3) + 3 * int(tile_y / 3)][num] -= 1

						rows[tile_x][cursor_mode] += 1
						columns[tile_y][cursor_mode] += 1
						blocks[int(tile_x / 3) + 3 * int(tile_y / 3)][cursor_mode] += 1
						filled_grid[tile_x][tile_y] = cursor_mode

				elif mouse_x >= num_offset - 27 and mouse_x < num_offset + 27:
					cursor_mode = int((mouse_y - 7) / tile_dim) + 1
				elif mouse_x >= 553 and mouse_x < 593 and mouse_y < 37:
					cursor_mode = 0

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_0: cursor_mode = 0
			elif event.key == pygame.K_1: cursor_mode = 1
			elif event.key == pygame.K_2: cursor_mode = 2
			elif event.key == pygame.K_3: cursor_mode = 3
			elif event.key == pygame.K_4: cursor_mode = 4
			elif event.key == pygame.K_5: cursor_mode = 5
			elif event.key == pygame.K_6: cursor_mode = 6
			elif event.key == pygame.K_7: cursor_mode = 7
			elif event.key == pygame.K_8: cursor_mode = 8
			elif event.key == pygame.K_9: cursor_mode = 9
			elif event.key == pygame.K_RETURN: 
				if check_finished(rows, columns, blocks):
					print("YOU WIN!!!!!!!")
					sys.exit()
				else:
					print("NOT DONE YET!")
