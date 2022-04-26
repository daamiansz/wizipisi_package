#wizipisipkg

import glob
import argparse
import os
import itertools
import errors
import sys
import tqdm
import sqlite3

def parser_package():
    parser = argparse.ArgumentParser(description='Pakowanie danych')
    parser.add_argument('tryb', type=str, help='podaj tryb dzialania; dostępne: pack', choices=['pack'])
    parser.add_argument('--src', type=str, help='podaj ściezkę do folderu z plikami lub pliku', required=True)
    parser.add_argument('--dest', type=str, help='podaj ściezkę do zapisu paczki wraz z nazwą bez rozszerzenia', required=True)
    parser.add_argument('--append', action=argparse.BooleanOptionalAction, help='użyj tej opcji jeżeli chcesz dodac zawartośc do paczki')
    return parser
    
def parser_unpackage():
    parser = argparse.ArgumentParser(description='Wypakowywanie danych')
    parser.add_argument('tryb', type=str, help='podaj tryb dzialania; dostępne: unpack', choices=['unpack'])
    parser.add_argument('--src', type=str, help='podaj ściezkę do paczki wraz z nazwą i rozszerzeniem .wizipisipkg', required=True)
    parser.add_argument('--dest', type=str, help='podaj ściezkę do docelowego folderu', required=True)
    parser.add_argument('--file_name', type=str, help='nazwa pojedynczego pliku wraz z rozszerzeniem [parametr opcjonalny]')
    return parser

def parser_get_files_list():
    parser = argparse.ArgumentParser(description='Pobieranie listy plików')
    parser.add_argument('tryb', type=str, help='podaj tryb dzialania; dostępne: get_files_list', choices=['get_files_list'])
    parser.add_argument('--src', type=str, help='podaj ściezkę do paczki wraz z nazwą i rozszerzeniem .wizipisipkg', required=True)
    parser.add_argument('--dest', type=str, help='podaj ściezkę i nazwę pliku z listą plików (bez rozszerzenia)', required=True)
    return parser

def get_files_list():
    args=parser_get_files_list().parse_args()
    if not os.path.isfile(args.src):
        raise errors.FileNameException.ObjectNotExist(args.object_path)
    conn=sqlite3.connect(args.src.split('.')[0]+'.wizipisiindex')
    c = conn.cursor()
    c.execute("select ident from indeksy;")
    with open(args.dest+'.txt', 'w') as f:
        f.write('\n'.join([i[0] for i in c.fetchall()]))

def packing():
    args=parser_package().parse_args()
    if args.append==None:
        if os.path.isfile(args.dest+'.wizipisipkg') or os.path.isfile(args.dest+'.wizipisiindex'):
            potwierdz=input("Czy napewno chcesz usunąć paczkę [T, N]: ").lower()
        else:
            potwierdz='t'
        if potwierdz in ['tak', 't', 'yes', 'y']:
            if os.path.isfile(args.dest+'.wizipisipkg'):
                os.remove(args.dest+'.wizipisipkg')
            if os.path.isfile(args.dest+'.wizipisiindex'):
                os.remove(args.dest+'.wizipisiindex')
            conn=sqlite3.connect(args.dest+'.wizipisiindex')
            c = conn.cursor()
            c.execute("create table indeksy (ident TEXT PRIMARY KEY, left_byte INTEGER, right_byte INTEGER);")
            conn.commit()
            conn.close()
        else:
            sys.exit(0)
    conn=sqlite3.connect(args.dest+'.wizipisiindex')
    if os.path.isfile(args.src):
        obiekty=[args.src]
    elif os.path.isdir(args.src):
        obiekty=glob.glob(args.src+'/*')
    else:
        raise errors.FileNameException.ObjectNotExist(args.object_path)
        
    for i in tqdm.tqdm(obiekty, total=len(obiekty)):
        if os.path.getsize(i)>0:
            file=open(i, 'rb').read()
            c = conn.cursor()
            c.execute("select right_byte from indeksy order by right_byte desc limit 1;")
            last_ind=c.fetchone()
            if last_ind==None:
                last_ind=0
            else:
                last_ind=last_ind[0]+1
            dst=args.dest.split('.')[0]
            with open(args.dest+'.wizipisipkg', 'ab') as f:
                c = conn.cursor()
                c.execute("insert into indeksy (ident, left_byte, right_byte) values('{0}', {1}, {2});".format(os.path.basename(i), last_ind, last_ind+len(file)-1))
                conn.commit()
                f.write(file)
    conn.close()

def unpacking():
    args=parser_unpackage().parse_args()

    src=args.src
    
    if '.wizipisipkg' not in src:
        src+='.wizipisipkg'
    
    src_ind=src.split('.')[0]+'.wizipisiindex'
    
    if not os.path.isfile(src) or not os.path.isfile(src_ind):
        raise FileNotFoundError
    
    conn=sqlite3.connect(src_ind)
    if args.file_name==None:
        c = conn.cursor()
        c.execute("select ident, left_byte, right_byte from indeksy;")
        data=c.fetchall()
        for ident, left_byte, right_byte in tqdm.tqdm(data, total=len(data)):
            with open('{0}/{1}'.format(args.dest, ident), 'wb') as f:
                with open(src, 'rb') as g:
                    g.seek(left_byte)
                    f.write(g.read(right_byte-left_byte))
    else:
        c = conn.cursor()
        c.execute("select ident, left_byte, right_byte from indeksy where ident='{0}';".format(args.file_name.replace(' ',' ')))
        wyn=c.fetchone()
        if wyn==None:
            raise errors.FileNameException.FileNameNotInPackage(args.file_name)
        ident, left_byte, right_byte=wyn
        with open('{0}/{1}'.format(args.dest, ident), 'wb') as f:
            with open(src, 'rb') as g:
                g.seek(left_byte)
                f.write(g.read(right_byte-left_byte))

    
def main(tryb):
    if tryb in ['--h', '-h', '--help', '--help']:
        print('''Wypakowywanie danych

positional arguments:
  {pack,unpack, get_files_list}         podaj tryb dzialania; dostępne: pack, unpack lub get_files_list''')
  
    elif tryb=='pack':
        packing()
    elif tryb=='unpack':
        unpacking()
    elif tryb == 'get_files_list':
        get_files_list()
    else:
        print("wybierz tryb działania: pack, unpack lub get_files_list")
        
main(sys.argv[1])