import subprocess
import sys

def run_script(script_name):
    print(f"\n{'='*40}\n正在执行: {script_name}\n{'='*40}")
    try:
        subprocess.run([sys.executable, f"scripts/{script_name}"], check=True)
        print(f"✅ {script_name} 执行成功！")
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} 执行失败，错误代码: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 开始一键复现 Olist 商业数据分析全流程...")
    run_script("01_load.py")
    run_script("02_clean.py")
    run_script("03_analysis.py")
    run_script("04_visuals.py")
    print("\n🎉 全流程复现完毕！请查看 outputs/ 文件夹。")
    print("💡 如需查看交互大屏，请在终端输入: streamlit run scripts/05_dashboard.py")