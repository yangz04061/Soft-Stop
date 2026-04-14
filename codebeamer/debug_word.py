import docx

def debug_paragraphs(docx_path):
    """
    Debug script to find key markers in the document.
    """
    doc = docx.Document(docx_path)
    all_paras = [p.text for p in doc.paragraphs]
    
    print(f"Total paragraphs: {len(all_paras)}\n")
    
    # Find key markers
    markers_to_find = [
        "陡坡缓降",
        "VMC的HDC",
        "功能架构",
        "功能激活",
        "功能逻辑策略概览",
        "显示策略",
        "法律法规"
    ]
    
    print("Searching for key markers:\n")
    for marker in markers_to_find:
        for i, para in enumerate(all_paras):
            if marker in para:
                print(f"Found '{marker}' at line {i}:")
                print(f"  Content: {para}\n")
                break

if __name__ == "__main__":
    docx_file = "SGMW_VMC HDC_陡坡缓降功能规范 Master_20260302.docx"
    debug_paragraphs(docx_file)