from tkinter import *
from tkinter import ttk, messagebox
from monitor_io import *
import datetime as d

root = Tk()

class Variables:
    memo_select = ('0',)
    schedule_select = ('0',)
    DAYS = {1:31, 2:28, -2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    this_year = d.datetime.now().year

# 컬럼명을 누르면 정렬되도록, 한번 더 누르면 역순으로 정렬되도록 기능을 추가하는 함수
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda _col=col: treeview_sort_column(tv, _col, not reverse))

# 조회 결과를 table로 만들어 gui창에 표시
def show_note(word, view_table):
    try:
        intword =str(int(word))
        search_result = search(sno4=intword)
    except:
        search_result = search(name=word)
    view_table.delete(*view_table.get_children())
    for i in range(len(search_result)):
        view_table.insert('', 'end', values=tuple(search_result[i].values()), iid=(i+1))
# 메모를 treeview에 보여주고 UI 처리
def show_memo(word, memo_table):
    try:
        search_result = get_memo(word)
        memo_table.delete(*memo_table.get_children())
        for i in range(len(search_result)):
            memo_table.insert('', 'end', values=tuple(search_result[i].values()), iid=int(search_result[i]['id']))
    except:
        messagebox.showerror('검색 실패', '검색 중 오류가 발생했습니다.')
# 스케줄을 treeview에 보여주고 UI 처리
def show_schedule(word, showall, start, end, schedule_table):
    try:
        search_result = view_schedule(word, start, end, all=showall)
        schedule_table.delete(*schedule_table.get_children())
        for i in range(len(search_result)):
            schedule_table.insert('', 'end', values=tuple(search_result[i].values()), iid=(i+1)*100000+int(search_result[i]['sno']))
    except:
        messagebox.showerror('검색 실패', '검색 중 오류가 발생했습니다.')

# 메모를 DB에 추가하고 UI 처리
def add_memo(name, type, memo):
    try:
        flag = insert_memo(name,type,memo)
    except:
        messagebox.showerror('추가 실패', '등록 중 오류가 발생했습니다.')
        return
    if flag:
        messagebox.showinfo('추가 완료', '성공적으로 추가되었습니다.')
    else:
        messagebox.showerror('추가 실패', '등록되지 않은 이름입니다.')
# 스케줄을 DB에 추가하고 UI 처리
def add_schedule(name, place, reason, start_time, end_time):
    #try:
    flag = insert_schedule(name, place, reason, start_time, end_time)
    #except:
    #    messagebox.showerror('추가 실패', '등록 중 오류가 발생했습니다.')
    #    return
    if flag:
        messagebox.showinfo('추가 완료', '성공적으로 추가되었습니다.')
    else:
        messagebox.showerror('추가 실패', '등록되지 않은 이름이거나 이미 다른 스케줄이 존재합니다.')

# 메모를 DB에서 삭제하고 UI 처리
def del_memo(id):
    try:
        delete_memo(id)
    except:
        messagebox.showerror('삭제 실패', '이미 존재하지 않는 데이터이거나 데이터를 선택하지 않았습니다.')
        return
    messagebox.showinfo('삭제 완료', '성공적으로 삭제되었습니다.')
# 스케줄을 DB에서 삭제하고 UI 처리
'''
def del_schedule(id, table):
    #try:
        for k in range(len(table.get_children())):
            i = table.item(table.get_children()[k])
            if k+1 == id//100000:
                point = i['values'][3]
                point = d.datetime.strptime(point, "%Y-%m-%d %H:%M:%S")
        r = cancel_schedule(id%100000, point)
        print(r)
    #except:
    #    messagebox.showerror('삭제 실패', '이미 존재하지 않는 데이터이거나 데이터를 선택하지 않았습니다.')
    #    return
    #messagebox.showinfo('삭제 완료', '성공적으로 삭제되었습니다.')
'''

# 메모 treeview에서 한 항목을 선택할 경우 그 id를 가져옴
def on_memo_select(event):
    Variables.memo_select = event.widget.selection()
    print(Variables.memo_select)

# 스케줄 treeview에서 한 항목을 선택할 경우 그 id를 가져옴
def on_schedule_select(event):
    Variables.schedule_select = event.widget.selection()
    print(Variables.schedule_select)

# 메인 창을 생성
def mainmenu():
    root.title('자감 일지 V1.0')
    root.resizable(0, 0)

    schedule_init()
    #3개의 탭창 생성
    tabControl = ttk.Notebook(root, width=600, height=630)
    note_tab = ttk.Frame(tabControl)
    memo_tab = ttk.Frame(tabControl)
    schedule_tab = ttk.Frame(tabControl)
    tabControl.add(note_tab, text="자감 일지")
    tabControl.add(memo_tab, text="자감 메모 조회")
    tabControl.add(schedule_tab, text="스케줄 조회")
    tabControl.pack(expand=1, fill="both")

    # note_tab(자감 일지 탭)
    search_frame = LabelFrame(note_tab, text='검색')
    search_frame.pack(padx=30, pady=10)
    view_frame = LabelFrame(note_tab, text="조회")
    view_frame.pack(padx=10, pady=10)
    # 자감 일지 내용을 보여주는 treeview
    view_table = ttk.Treeview(view_frame, columns=['학년', '반', '번호', '이름', 'S', 'T', 'W', 'Z','H'],)
    view_table.pack(padx=10, pady=10)
    view_table.column("#0", width=0, stretch=NO)
    for col, wid in zip(view_table['columns'], [50, 50 ,50, 100, 50, 50, 50, 50, 50]):
        view_table.column(col, width=wid, stretch=NO)
    for col in view_table['columns']:
        view_table.heading(col, text=col,command=lambda _col=col: treeview_sort_column(view_table, _col, False))

    # 검색창
    search_var = StringVar()
    search_box = Entry(search_frame, width=20, font=('맑은 고딕', 14), textvariable=search_var)
    search_box.grid(row=0, column=0, padx=5, pady=5)
    search_button = Button(search_frame, font=('맑은 고딕', 14), text='검색', command=lambda: show_note(search_var.get(), view_table))
    search_button.grid(row=0, column=1, padx=5, pady=5)

    # memo_tab(메모 조회 탭)
    search_memo_frame = LabelFrame(memo_tab, text='검색')
    search_memo_frame.pack(padx=30, pady=10)
    memo_frame = LabelFrame(memo_tab, text="조회")
    memo_frame.pack(padx=10, pady=10)

    # 메모 내용을 보여주는 treeview
    memo_table = ttk.Treeview(memo_frame, columns=['연번', '유형', '메모', '기록 시각'],)
    memo_table.pack(padx=10, pady=10)
    memo_table.column("#0", width=0, stretch=NO)
    for col, wid in zip(memo_table['columns'], [50, 50, 200, 150]):
        memo_table.column(col, width=wid, stretch=NO)
    for col in memo_table['columns']:
        memo_table.heading(col, text=col,command=lambda _col=col: treeview_sort_column(memo_table, _col, False))
    memo_table.bind('<<TreeviewSelect>>', on_memo_select)

    delete_memo_button = Button(memo_frame, font=('맑은 고딕', 14), text='삭제', command=lambda: del_memo(int(Variables.memo_select[0])))
    delete_memo_button.pack(padx=5, pady=5)


    # 검색 및 메모 입력창
    search_memo_var = StringVar()
    search_memo_box = Entry(search_memo_frame, width=20, font=('맑은 고딕', 14), textvariable=search_memo_var)
    search_memo_box.grid(row=0, column=1, padx=5, pady=5)
    search_memo_button = Button(search_memo_frame, font=('맑은 고딕', 14), text='검색', command=lambda: show_memo(search_memo_var.get(), memo_table))
    search_memo_button.grid(row=0, column=2, padx=5, pady=5)

    add_type_var = StringVar()
    add_memo_combobox = ttk.Combobox(search_memo_frame, width=10, textvariable=add_type_var, state='readonly')
    add_memo_combobox['values'] = ('-', 's', 't', 'w', 'z', 'h')
    add_memo_combobox.current(0)
    add_memo_combobox.grid(row=1, column=0, padx=5, pady=5)

    add_memo_var = StringVar()
    add_memo_box = Entry(search_memo_frame, width=20, font=('맑은 고딕', 14), textvariable=add_memo_var)
    add_memo_box.grid(row=1, column=1, padx=5, pady=5)
    add_memo_button = Button(search_memo_frame, font=('맑은 고딕', 14), text='추가', command=lambda: add_memo(search_memo_var.get(),add_type_var.get(),add_memo_var.get()))
    add_memo_button.grid(row=1, column=2, padx=5, pady=5)

    search_memo_frame.grid_columnconfigure(0, weight=1)
    search_memo_frame.grid_columnconfigure(1, weight=3)
    search_memo_frame.grid_columnconfigure(2, weight=3)

    # schedule_tab(스케줄 조회 탭)
    search_schedule_frame = LabelFrame(schedule_tab, text='검색')
    search_schedule_frame.pack(padx=30, pady=10)
    add_schedule_frame = LabelFrame(schedule_tab, text='추가')
    add_schedule_frame.pack(padx=30, pady=10)
    schedule_frame = LabelFrame(schedule_tab, text="조회")
    schedule_frame.pack(padx=10, pady=10)

    # 메모 내용을 보여주는 treeview
    schedule_table = ttk.Treeview(schedule_frame, columns=['연번', '스케줄명', '상세', '시작 시각', '종료 시각'],)
    schedule_table.pack(padx=10, pady=10)
    schedule_table.column("#0", width=0, stretch=NO)
    for col, wid in zip(schedule_table['columns'], [0, 100, 150, 125, 125]):
        schedule_table.column(col, width=wid, stretch=NO)
    for col in schedule_table['columns']:
        schedule_table.heading(col, text=col,command=lambda _col=col: treeview_sort_column(schedule_table, _col, False))
    schedule_table.bind('<<TreeviewSelect>>', on_schedule_select)
    '''
    delete_schedule_button = Button(schedule_frame, font=('맑은 고딕', 14), text='삭제', command=lambda: del_schedule(int(Variables.schedule_select[0]), schedule_table))
    delete_schedule_button.pack(padx=5, pady=5)
    '''

    # 검색 및 스케줄 입력창

    start_year_var = StringVar()
    start_year_combobox = ttk.Combobox(add_schedule_frame, width=5, textvariable=start_year_var)
    start_year_combobox['values'] =tuple(range(Variables.this_year, Variables.this_year+2))
    start_year_combobox.current(0)
    start_year_combobox.grid(row=0, column=0, padx=5, pady=5)
    start_year_label=Label(add_schedule_frame, text="년", width=2)
    start_year_label.grid(row=0, column=1, padx=5, pady=5)

    start_month_var = StringVar()
    start_month_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=start_month_var)
    start_month_combobox['values']= tuple(range(1, 13))
    start_month_combobox.current(0)
    start_month_combobox.grid(row=0, column=2, padx=5, pady=5)
    start_month_label=Label(add_schedule_frame, text="월", width=2)
    start_month_label.grid(row=0, column=3, padx=5, pady=5)

    start_day_var = StringVar()
    start_day_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=start_day_var)
    start_day_combobox['values'] = tuple(range(1, Variables.DAYS[-2 if (int(start_month_var.get()) == 2) and ((int(start_year_var.get()) % 4 == 0)
    or (int(start_year_var.get()) % 100 != 0 and int(start_year_var.get()) % 400 == 0)) else int(start_month_var.get())]+1))
    start_day_combobox.current(0)
    start_day_combobox.grid(row=0, column=4, padx=5, pady=5)
    start_day_label=Label(add_schedule_frame, text="일", width=2)
    start_day_label.grid(row=0, column=5, padx=5, pady=5)

    start_hour_var = StringVar()
    start_hour_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=start_hour_var)
    start_hour_combobox['values'] = tuple(range(24))
    start_hour_combobox.current(0)
    start_hour_combobox.grid(row=0, column=6, padx=5, pady=5)
    start_hour_label=Label(add_schedule_frame, text="시", width=2)
    start_hour_label.grid(row=0, column=7, padx=5, pady=5)

    start_min_var = StringVar()
    start_min_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=start_min_var)
    start_min_combobox['values'] = tuple(range(60))
    start_min_combobox.current(0)
    start_min_combobox.grid(row=0, column=8, padx=5, pady=5)
    start_min_label=Label(add_schedule_frame, text="분  ~", width=5)
    start_min_label.grid(row=0, column=9, padx=5, pady=5)

    end_year_var = StringVar()
    end_year_combobox = ttk.Combobox(add_schedule_frame, width=5, textvariable=end_year_var)
    end_year_combobox['values'] =tuple(range(Variables.this_year, Variables.this_year+2))
    end_year_combobox.current(0)
    end_year_combobox.grid(row=1, column=0, padx=5, pady=5)
    end_year_label=Label(add_schedule_frame, text="년", width=2)
    end_year_label.grid(row=1, column=1, padx=5, pady=5)

    end_month_var = StringVar()
    end_month_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=end_month_var)
    end_month_combobox['values']= tuple(range(1, 13))
    end_month_combobox.current(0)
    end_month_combobox.grid(row=1, column=2, padx=5, pady=5)
    end_month_label=Label(add_schedule_frame, text="월", width=2)
    end_month_label.grid(row=1, column=3, padx=5, pady=5)

    end_day_var = StringVar()
    end_day_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=end_day_var)
    end_day_combobox['values'] = tuple(range(1, Variables.DAYS[-2 if (int(start_month_var.get()) == 2) and ((int(start_year_var.get()) % 4 == 0)
    or (int(start_year_var.get()) % 100 != 0 and int(start_year_var.get()) % 400 == 0)) else int(start_month_var.get())]+1))
    end_day_combobox.current(0)
    end_day_combobox.grid(row=1, column=4, padx=5, pady=5)
    end_day_label=Label(add_schedule_frame, text="일", width=2)
    end_day_label.grid(row=1, column=5, padx=5, pady=5)

    end_hour_var = StringVar()
    end_hour_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=end_hour_var)
    end_hour_combobox['values'] = tuple(range(24))
    end_hour_combobox.current(0)
    end_hour_combobox.grid(row=1, column=6, padx=5, pady=5)
    end_hour_label=Label(add_schedule_frame, text="시", width=2)
    end_hour_label.grid(row=1, column=7, padx=5, pady=5)

    end_min_var = StringVar()
    end_min_combobox = ttk.Combobox(add_schedule_frame, width=3, textvariable=end_min_var)
    end_min_combobox['values'] = tuple(range(60))
    end_min_combobox.current(0)
    end_min_combobox.grid(row=1, column=8, padx=5, pady=5)
    end_min_label=Label(add_schedule_frame, text="분", width=5)
    end_min_label.grid(row=1, column=9, padx=5, pady=5)

    add_place_label = Label(add_schedule_frame, width=3, text="장소", font=('맑은 고딕', 14))
    add_place_label.grid(row=2, column=0, padx=5, pady=5)
    add_place_var = StringVar()
    add_place_box = Entry(add_schedule_frame, width=13, font=('맑은 고딕', 14), textvariable=add_place_var)
    add_place_box.grid(row=2, column=1, columnspan=5, padx=5, pady=5)

    add_reason_label = Label(add_schedule_frame, width=6, text="스케줄명", font=('맑은 고딕', 14))
    add_reason_label.grid(row=2, column=6, padx=5, pady=5)
    add_reason_var = StringVar()
    add_reason_box = Entry(add_schedule_frame, width=13, font=('맑은 고딕', 14), textvariable=add_reason_var)
    add_reason_box.grid(row=2, column=7, columnspan=5, padx=5, pady=5)

    add_schedule_button = Button(add_schedule_frame, font=('맑은 고딕', 14), text='추가', command=lambda: add_schedule(search_schedule_var.get(),add_place_var.get(),add_reason_var.get(),
    d.datetime(int(start_year_var.get()), int(start_month_var.get()), int(start_day_var.get()), int(start_hour_var.get()), int(start_min_var.get())),
    d.datetime(int(end_year_var.get()), int(end_month_var.get()), int(end_day_var.get()), int(end_hour_var.get()), int(end_min_var.get()))))
    add_schedule_button.grid(row=3, column=0, padx=5, pady=5)

    is_allrange = IntVar()
    search_schedule_var = StringVar()
    search_schedule_box = Entry(search_schedule_frame, width=20, font=('맑은 고딕', 14), textvariable=search_schedule_var)
    search_schedule_box.grid(row=0, column=0, padx=5, pady=5)
    search_schedule_button = Button(search_schedule_frame, font=('맑은 고딕', 14), text='검색', command=lambda: show_schedule(search_schedule_var.get(), is_allrange.get(),
    d.datetime(int(start_year_var.get()), int(start_month_var.get()), int(start_day_var.get()), int(start_hour_var.get()), int(start_min_var.get())),
    d.datetime(int(end_year_var.get()), int(end_month_var.get()), int(end_day_var.get()), int(end_hour_var.get()), int(end_min_var.get())), schedule_table))
    search_schedule_button.grid(row=0, column=1, padx=5, pady=5)
    all_range_check = Checkbutton(search_schedule_frame, text='모든 스케줄 표시', var=is_allrange)
    all_range_check.grid(row=0, column=2, padx=5, pady=5)
    all_range_check.toggle()


    root.mainloop()
