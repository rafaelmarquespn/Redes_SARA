from playwright.sync_api import Playwright, sync_playwright, expect
import json

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://164.41.67.41/DASHDatasetTest/BigBuckBunny/1sec/")
    
    tamanhos = {}
    count = 0
    for linha in range(4, (page.locator("tbody").locator("tr").count()-2)):
        page.locator('tr').nth(linha).locator('td').nth(1).locator('a').click()
        lista_tamanhos = []
        for line in range(3,page.locator("tbody").locator("tr").count()):
            try:
                teste = page.locator('tr').nth(line).locator('td').nth(1).inner_text(timeout=1000) 
            except:
                continue
            if 'mp4' in teste:
                print(teste)
                continue
            else:
                tamanho = page.locator('tr').nth(line).locator('td').nth(3).inner_text()
                print(tamanho)
                if '.' in tamanho and 'M' in tamanho:
                    tamanho = tamanho.replace('.', '')
                    tamanho = tamanho.replace('M', '')
                    tamanho = int(tamanho)*100000
                elif '.' in tamanho and 'K' in tamanho:
                    tamanho = tamanho.replace('.', '')
                    tamanho = tamanho.replace('K', '')
                    tamanho = int(tamanho)*100
                elif 'M' in tamanho and '.' not in tamanho:
                    tamanho = tamanho.replace('M', '') 
                    int(tamanho)*1000000
                elif 'K' in tamanho and '.' not in tamanho:
                    tamanho = tamanho.replace('K', '')
                    tamanho = int(tamanho)*1000

                tamanho = int(tamanho)
                tamanho = tamanho * 8 
                print(tamanho)
                lista_tamanhos.append(tamanho)
        tamanhos[count] = lista_tamanhos
        count += 1
        page.go_back()
    with open(f'.\\lista_tamanhos.json', 'w',encoding='utf-8') as arquivo:
        arquivo.write(json.dumps(tamanhos, indent=4))
    print(tamanhos)
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
