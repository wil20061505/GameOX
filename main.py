import state as st
import cauhinh
import pygame
import sys
from typing import Optional, List, Tuple

pygame.init()
# Trạng thái game
FONT_BIG = pygame.font.SysFont(None, 72)
FONT_MED = pygame.font.SysFont(None, 36) 
FONT_SMALL = pygame.font.SysFont(None, 24)
 
trang_thai = st.state.menu # mặc định là menu
active_mode = None # lưu chế độ chơi hiện tại để reset
display_mode = True # lưu chế độ hiện thị mặc định là dark mode(true)
screen = pygame.display.set_mode(cauhinh.WINDOW_SIZE)
pygame.display.set_caption("TIK TAC TOK")


# bàn chơi
board = [['' for i in range(3)] for i in range(3)]
current = 'X'
game_over = False
winner = None
winning_line: Optional[List[Tuple[int, int]]] = None

# ----Hàm phụ

# reset game
def reset_game():
    global board, current, game_over, winner, winning_line
    board = [['' for _ in range(3)] for _ in range(3)]
    current = 'X'
    game_over = False
    winner = None
    winning_line = None

# lấy vị trí chuột
def pos_to_cell(pos):
    x, y = pos
    if y >= cauhinh.SIZE:
        return None
    col = x // cauhinh.CELL
    row = y // cauhinh.CELL
    return row, col

# hàm tra về giá trị đúng sai
def button_clicked(pos, rect):
    x, y = pos
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh

# ---- hàm chính

# vẽ nút
def draw_button(rect,text):
    x,y,w,h = rect
    pygame.draw.rect(screen,cauhinh.PANEL_COLOR,rect,border_radius = 8)
    pygame.draw.rect(screen, cauhinh.LINE_COLOR, rect, 4, border_radius=8)
    txt = FONT_MED.render(text, True, (255, 255, 0))
    screen.blit(txt, txt.get_rect(center=(x + w // 2, y + h // 2)))
# vẽ menu
def draw_menu():
    # vẽ giao diện mở đầu
    screen.fill(cauhinh.BG_COLOR)
    title = FONT_BIG.render("Caro 3x3",True,cauhinh.TEXT_COLOR)
    sup = FONT_MED.render("Menu",True,cauhinh.TEXT_COLOR)
    screen.blit(title,title.get_rect(center = (cauhinh.SIZE //2 , 80)))
    screen.blit(sup,sup.get_rect(center = (cauhinh.SIZE //2 , 140)))
    # vẽ nút
    draw_button((cauhinh.SIZE // 2 - 140, 200, 280, 50), "TWO PLAYER")
    draw_button((cauhinh.SIZE // 2 - 140, 270, 280, 50), "SINGLE PLAYER")
    draw_button((cauhinh.SIZE // 2 - 140, 340, 280, 40), "Close")

    # viết dòng note
    note = [
        "DAT studio"
    ]
    for i, ln in enumerate(note):
        txt = FONT_SMALL.render(ln,True,cauhinh.TEXT_COLOR)
        screen.blit(txt,(10,cauhinh.SIZE + 10 + i*20))
    
    # chạy lên mình hình
    pygame.display.flip()

#vẽ giao diện game
def draw_board_ui ():
    screen.fill(cauhinh.BG_COLOR)

    # vẽ bàng cờ
    pygame.draw.rect(screen,cauhinh.PANEL_COLOR,(0,cauhinh.SIZE,cauhinh.SIZE,cauhinh.INFO_HEIGHT))

    #vẽ lưới 
    for i in range(1,3):
        pygame.draw.line(screen,cauhinh.LINE_COLOR,(0,cauhinh.CELL * i),(cauhinh.SIZE,cauhinh.CELL * i),4)
        pygame.draw.line(screen,cauhinh.LINE_COLOR,(cauhinh.CELL * i,0),(cauhinh.CELL * i,cauhinh.SIZE),4)
    
    #vẽ các kí hiệu X O
        for y in range(3):
            for x in range(3):
                symbol = board[y][x]
                if symbol:
                    txt = FONT_BIG.render(symbol, True, (cauhinh.X_COLOR if symbol == 'X' else cauhinh.O_COLOR))
                    rect = txt.get_rect(center=(x * cauhinh.CELL + cauhinh.CELL // 2, y * cauhinh.CELL + cauhinh.CELL // 2))
                    screen.blit(txt, rect)
        # vẽ các đường thắng nếu có
        if winning_line is not None and winner != 'Draw':
            (r1, c1), (r2, c2), (r3, c3) = winning_line
            start = (c1 * cauhinh.CELL + cauhinh.CELL // 2, r1 * cauhinh.CELL + cauhinh.CELL // 2)
            end = (c3 * cauhinh.CELL + cauhinh.CELL // 2, r3 * cauhinh.CELL + cauhinh.CELL // 2)
            pygame.draw.line(screen, (255, 255, 0), start, end, 6)
        # Vùng thông tin dưới cùng
        mode_text = "TWO PLAYER" if active_mode == st.state.play_humman else "SINGLE PLAYER" if active_mode == st.state.play_AI else "NONE"
        info = f"MODE: {mode_text}"
        info2 =  f"Turn: {current}"
        txt_info = FONT_SMALL.render(info, True, (255, 255, 0))
        txt_info2 = FONT_SMALL.render(info2, True, cauhinh.TEXT_COLOR)
        screen.blit(txt_info, (10, cauhinh.SIZE + 10))
        screen.blit(txt_info2, (10, cauhinh.SIZE + 30))
        # Nút Chơi lại và Về menu
        draw_button((cauhinh.SIZE - 200, cauhinh.SIZE + 10, 90, 40), "Restart")
        draw_button((cauhinh.SIZE - 100, cauhinh.SIZE + 10, 90, 40), "Menu")
    
    pygame.display.flip()
    # vẽ chiến thắng
def draw_result():
    draw_board_ui()
    overlay = pygame.Surface((cauhinh.SIZE, cauhinh.SIZE), pygame.SRCALPHA)
    overlay.fill((102, 255, 204, 180))
    screen.blit(overlay, (0, 0))

    if winner == 'Draw':
        msg = "Draw"
    else:
        msg = f"{winner} WIN!"
    txt = FONT_BIG.render(msg, True, (255, 255, 0))
    screen.blit(txt, txt.get_rect(center=(cauhinh.SIZE // 2, cauhinh.SIZE // 2 - 20)))
    hint = FONT_MED.render("Choose 'Restart' or 'Menu'", True, (255, 0, 0))
    screen.blit(hint, hint.get_rect(center=(cauhinh.SIZE // 2, cauhinh.SIZE // 2 + 40)))
    pygame.display.flip()
        
# --- Logic game ---

def check_win():
    global winning_line
    winning_line = None
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != '':
            winning_line = [(i, 0), (i, 1), (i, 2)]
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != '':
            winning_line = [(0, i), (1, i), (2, i)]
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != '':
        winning_line = [(0, 0), (1, 1), (2, 2)]
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        winning_line = [(0, 2), (1, 1), (2, 0)]
        return board[0][2]
    if all(board[y][x] != '' for y in range(3) for x in range(3)):
        return 'Draw'
    return None


def minimax(is_maximizing):
    w = check_win()
    if w == 'O':
        return 1
    if w == 'X':
        return -1
    if w == 'Draw':
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for y in range(3):
            for x in range(3):
                if board[y][x] == '':
                    board[y][x] = 'O'
                    score = minimax(False)
                    board[y][x] = ''
                    if score > best_score:
                        best_score = score
        return best_score
    else:
        best_score = float('inf')
        for y in range(3):
            for x in range(3):
                if board[y][x] == '':
                    board[y][x] = 'X'
                    score = minimax(True)
                    board[y][x] = ''
                    if score < best_score:
                        best_score = score
        return best_score


def ai_move():
    best_score = -float('inf')
    move = None
    for y in range(3):
        for x in range(3):
            if board[y][x] == '':
                board[y][x] = 'O'
                score = minimax(False)
                board[y][x] = ''
                if score > best_score:
                    best_score = score
                    move = (y, x)
    if move:
        board[move[0]][move[1]] = 'O'
# --- Vòng lặp chính ---
clock = pygame.time.Clock()

while True:
    if trang_thai == st.state.menu:
        draw_menu()
    elif trang_thai in (st.state.play_humman, st.state.play_AI):
        draw_board_ui()
    elif trang_thai == st.state.result:
        draw_result()     # KHÔNG chạy draw_board_ui() nữa

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if trang_thai == st.state.menu:
                # 3 nút menu (vị trí tương ứng với draw_menu)
                if button_clicked((mx, my), (cauhinh.SIZE // 2 - 140, 200, 280, 50)):
                    reset_game()
                    active_mode = st.state.play_humman
                    trang_thai = active_mode
                elif button_clicked((mx, my), (cauhinh.SIZE // 2 - 140, 270, 280, 50)):
                    reset_game()
                    active_mode = st.state.play_AI
                    trang_thai = active_mode
                elif button_clicked((mx, my), (cauhinh.SIZE // 2 - 140, 340, 280, 40)):
                    pygame.quit()
                    sys.exit()

            elif trang_thai in (st.state.play_humman, st.state.play_AI) and not game_over:
                # Nút Chơi lại
                if button_clicked((mx, my), (cauhinh.SIZE - 200, cauhinh.SIZE + 10, 90, 40)):
                    reset_game()
                    # giữ nguyên active_mode, chuyển trang_thai về active_mode
                    if active_mode:
                        trang_thai = active_mode
                    else:
                        trang_thai = st.state.play_humman
                    continue
                # Nút Menu
                if button_clicked((mx, my), (cauhinh.SIZE - 100, cauhinh.SIZE + 10, 90, 40)):
                    reset_game()
                    trang_thai = st.state.menu
                    active_mode = None
                    continue

                cell = pos_to_cell((mx, my))
                if cell:
                    r, c = cell
                    if board[r][c] == '':
                        board[r][c] = current
                        w = check_win()
                        if w:
                            game_over = True
                            winner = w
                            trang_thai = st.state.result
                        else:
                            if trang_thai == st.state.play_humman:
                                current = 'O' if current == 'X' else 'X'
                            else:  # PLAY_AI
                                # Sau lượt người (X), máy đi (O)
                                ai_move()
                                w = check_win()
                                if w:
                                    game_over = True
                                    winner = w
                                    trang_thai = st.state.result
                                else:
                                    current = 'X'

            elif trang_thai == st.state.result:
                # Nút Chơi lại
                if button_clicked((mx, my), (cauhinh.SIZE - 200, cauhinh.SIZE + 10, 90, 40)):
                    reset_game()
                    # chuyển về chế độ lưu trong active_mode
                    if active_mode:
                        trang_thai = active_mode
                    else:
                        trang_thai = st.state.play_humman
                if button_clicked((mx, my), (cauhinh.SIZE - 100, cauhinh.SIZE + 10, 90, 40)):
                    reset_game()
                    trang_thai = st.state.menu
                    active_mode = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                if active_mode:
                    trang_thai = active_mode
                else:
                    trang_thai = st.state.play_humman
            if event.key == pygame.K_ESCAPE:
                reset_game()
                trang_thai = st.state.menu
                active_mode = None

    # Nếu game over do AI hoặc người làm, đảm bảo hiển thị màn kết quả
    if not game_over:
        w = check_win()
        if w:
            game_over = True
            winner = w
            trang_thai = st.state.result
    if trang_thai == st.state.result:
        clock.tick(5)
    else:
        clock.tick(60)

