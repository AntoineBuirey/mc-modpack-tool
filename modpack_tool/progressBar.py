
import os

class ProgressBar:
    """
    A progress bar class to display the progress of a task in the bottom of the console.
    Support auto-resizing of the console window and dynamic updates to the progress bar.
    Also supports sub-progress bars for nested tasks (subbars are displayed above the main progress bar).
    """
    
    def __init__(self,
                 total: int,
                 label: str = '',
                 fill: str = '█',
                 use_percentage: bool = True,
                 _nested_level: int = 0):
        self.__total = total
        self.__label = label
        self.__fill = fill
        self.__current = 0
        self.__subbar : ProgressBar | None = None
        self.__use_percentage = use_percentage
        self.__nested_level = _nested_level
        self.display()  # Display the progress bar immediately upon initialization
        
    @staticmethod
    def hide_cursor():
        print("\033[?25l", end='')  # Hide cursor
        
    @staticmethod
    def show_cursor():
        print("\033[?25h", end='')  # Show cursor
        
    def __del__(self):
        self.clear()
        
    def clear(self):
        print(f"\033[s", end='')  # Save cursor position
        print(f"\033[H\033[{self.__get_term_height() - 1 - self.__nested_level}E", end='')  # Move cursor to the bottom of the console
        print(' '*self.__get_term_width(), end='\r', flush=True)
        print("\033[u", end='')  # Restore cursor position
        
    def update(self, progress: int = 1):
        self.__current += progress
        if self.__current > self.__total:
            self.__current = self.__total
        self.display()
        
    def __add__(self, progress: int):
        self.update(progress)
        return self
    
    def __get_term_width(self):
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80  # Default width if terminal size cannot be determined
        
    def __get_term_height(self):
        try:
            return os.get_terminal_size().lines
        except OSError:
            return 24  # Default height if terminal size cannot be determined

    
    def set_subbar(self, total: int, label: str = '', use_percentage : bool|None = None) -> 'ProgressBar':
        if self.__subbar is not None:
            raise ValueError("A subbar is already set. Only one subbar is supported at a time.")
        subbar = ProgressBar(total,
                             label,
                             self.__fill,
                             use_percentage = use_percentage if use_percentage is not None else self.__use_percentage,
                             _nested_level = self.__nested_level + 1)
        self.__subbar = subbar
        return subbar
    
    def remove_subbar(self):
        if self.__subbar is None:
            raise ValueError("No subbar to remove.")
        self.__subbar.clear()
        self.__subbar = None
        
    @property
    def subbar(self) -> 'ProgressBar | None':
        return self.__subbar
    
    
    def display(self):
        # first, go to the bottom of the console, minus the number parent subbars (nested levels)
        term_height = self.__get_term_height() - 1
        ProgressBar.hide_cursor()
        # save position
        print(f"\033[s", end='')  # Save cursor position
        print(f"\033[H\033[{term_height - self.__nested_level}E", end='')  # Move cursor to the bottom of the console
        

        # then, display the main progress bar
        term_width = self.__get_term_width()
        bar_width = term_width - len(self.__label) - 11
        filled_length = int(bar_width * self.__current // self.__total)
        percentage = (self.__current / self.__total) * 100
        bar = self.__fill * filled_length + '-' * (bar_width - filled_length)
        if self.__use_percentage:
            print(f"{self.__label} |{bar}| {percentage:.2f}%", flush=True, end='')
        else:
            print(f"{self.__label} |{bar}| {self.__current}/{self.__total}", flush=True, end='')
        
        # reset cursor position
        print(f"\033[u", end='')  # Restore cursor position
        ProgressBar.show_cursor()
        
        
        
        
if __name__ == "__main__":
    import time
    main_bar = ProgressBar(100, "Main Task")
    
    for i in range(100):
        time.sleep(0.1)
        main_bar.update(1)
        if i == 30 or i == 60:
            sub_bar = main_bar.set_subbar(50, "Sub Task")
            for j in range(50):
                time.sleep(0.05)
                sub_bar.update(1)
            main_bar.remove_subbar()
    