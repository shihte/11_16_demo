from pathlib import Path

class CaesarCipher:
    def __init__(self, shift=3):
        self.shift = shift
    
    def encrypt(self, text):
        result = ""
        for char in text:
            if char.isascii():  # 只處理ASCII字符
                ascii_val = ord(char)
                shifted = (ascii_val + self.shift) % 256
                result += chr(shifted)
            else:
                result += char
        return result

class FileProcessor:
    def __init__(self, directory_path, shift=3):
        self.directory = Path(directory_path)
        self.cipher = CaesarCipher(shift)
        self.SUFFIX = ".hello"
    
    def process_file(self, file_path):
        """處理單個文件"""
        try:
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # 加密內容
            processed_content = self.cipher.encrypt(content)
            new_path = file_path.with_suffix(file_path.suffix + self.SUFFIX)
            
            # 寫入處理後的內容
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # 刪除原文件
            file_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"處理文件 {file_path} 時發生錯誤: {str(e)}")
            return False
    
    def process_directory(self):
        """處理整個目錄"""
        processed_files = 0
        failed_files = 0
        
        if not self.directory.exists():
            raise ValueError(f"目錄 {self.directory} 不存在")
        
        # 選擇要處理的文件
        files = [f for f in self.directory.rglob("*") 
                if f.is_file() and not f.suffix.endswith(self.SUFFIX)
                and not f.name.startswith('.')]
        
        for file_path in files:
            print(f"正在處理: {file_path}")
            if self.process_file(file_path):
                processed_files += 1
            else:
                failed_files += 1
        
        return processed_files, failed_files

def main():
    print("\n=== 文件加密工具 ===")
    directory = input("請輸入目錄路徑: ")
    shift = int(input("請輸入位移量 (默認為3): ") or "3")
    
    processor = FileProcessor(directory, shift)
    
    try:
        processed, failed = processor.process_directory()
        print(f"\n處理完成:")
        print(f"成功處理文件數: {processed}")
        print(f"失敗文件數: {failed}")
        
    except Exception as e:
        print(f"發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()