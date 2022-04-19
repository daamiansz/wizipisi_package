#wizipisipkg

import glob
import argparse
import os
import itertools
import errors
import sys

            
def parser_package():
    parser = argparse.ArgumentParser(description='Pakowanie danych')
    parser.add_argument('tryb', type=str, help='podaj tryb dzialania; dostępne: pack lub unpack', choices=['pack', 'unpack'])
    parser.add_argument('--src', type=str, help='podaj ściezkę do folderu z plikami lub pliku', required=True)
    parser.add_argument('--dest', type=str, help='podaj ściezkę do zapisu paczki wraz z nazwą bez rozszerzenia', required=True)
    parser.add_argument('--append', action=argparse.BooleanOptionalAction, help='użyj tej opcji jeżeli chcesz dodac zawartośc do paczki')
    return parser
    
def parser_unpackage():
    parser = argparse.ArgumentParser(description='Wypakowywanie danych')
    parser.add_argument('tryb', type=str, help='podaj tryb dzialania; dostępne: pack lub unpack', choices=['pack', 'unpack'])
    parser.add_argument('--src', type=str, help='podaj ściezkę do paczki wraz z nazwą i rozszerzeniem', required=True)
    parser.add_argument('--dest', type=str, help='podaj ściezkę do docelowego folderu', required=True)
    parser.add_argument('--file_name', type=str, help='nazwa pojedynczego pliku wraz z rozszerzeniem')
    return parser
    
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
        else:
            sys.exit(0)

    if os.path.isfile(args.src):
        obiekty=[args.src]
    elif os.path.isdir(args.src):
        obiekty=glob.iglob(args.src+'/*')
    else:
        raise errors.FileNameException.ObjectNotExist(args.object_path)
        
    for i in obiekty:
        file=open(i, 'rb').read()
        if not os.path.isfile(args.dest+'.wizipisiindex'):
            last_ind=0
        else:
            last_ind=int(open(args.dest+'.wizipisiindex', 'r').readlines()[-1][:-1].split(';')[-1])+1
        dst=args.dest.split('.')[0]
        with open(args.dest+'.wizipisipkg', 'ab') as f:
            with open(args.dest+'.wizipisiindex', 'a') as g:
                g.write("{0};{1};{2}\n".format(os.path.basename(i), last_ind, last_ind+len(file)-1))
            f.write(file)


def unpacking():
    args=parser_unpackage().parse_args()

    src=args.src
    
    if '.wizipisipkg' not in src:
        src+='.wizipisipkg'
    
    src_ind=src.split('.')[0]+'.wizipisiindex'
    
    if not os.path.isfile(src) or not os.path.isfile(src_ind):
        raise FileNotFoundError
    indeks={i.split(';')[0]:list(map(int, i[:-1].split(';')[1:])) for i in open(src_ind, 'r').readlines()}

    if args.file_name==None:
        for key, value in indeks.items():
            with open('{0}/{1}'.format(args.dest, key), 'wb') as f:
                with open(src, 'rb') as g:
                    g.seek(value[0])
                    f.write(g.read(value[1]-value[0]))
    else:
        if args.file_name not in indeks:
            raise errors.FileNameException.FileNameNotInPackage(args.file_name)
        with open('{0}/{1}'.format(args.dest, args.file_name), 'wb') as f:
            with open(src, 'rb') as g:
                g.seek(indeks[args.file_name][0])
                f.write(g.read(indeks[args.file_name][1]-indeks[args.file_name][0]))


    
def main(tryb):
    if tryb in ['--h', '-h', '--help', '--help']:
        print('''Wypakowywanie danych

positional arguments:
  {pack,unpack}         podaj tryb dzialania; dostępne: pack lub unpack''')
  
    elif tryb=='pack':
        packing()
    elif tryb=='unpack':
        unpacking()
    else:
        print("wybierz tryb działania: pack, unpack lub append")
        
main(sys.argv[1])