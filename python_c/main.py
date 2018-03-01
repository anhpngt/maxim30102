import maxim

def main():
    result = [float('nan'), float('nan')]
    if(maxim.calculate([1, 2], [3, 4], result)):
        print(result)
    else:
        print('Unable to calculate!')

if __name__ == "__main__":
    main()