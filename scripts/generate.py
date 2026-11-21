#!/usr/bin/env python3
"""每天生成12栏文章并更新网站数据；Python 标准库，无需安装依赖。"""
import datetime as dt
import json
import os
import pathlib
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "issues.json"
DATE = dt.datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
COLUMNS = [
    "世界级设计案例", "颠覆认知的知识", "实用小工具",
    "私人历史博物馆", "AI与开源工具", "高级配色与材质",
    "思维挑战", "电影与纪录片", "特色植物研究",
    "哲学辩论", "普通物品重新设计", "世界情报",
]
FEEDS = [
    "https://www.sciencedaily.com/rss/top/science.xml",
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "https://www.nasa.gov/feed/",
]
def news():
    found = []
    for feed in FEEDS:
        try:
            req = urllib.request.Request(feed, headers={"User-Agent": "TwelveInspirations/1.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                doc = ET.fromstring(r.read(600_000))
            for item in doc.findall(".//item")[:12]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                date = (item.findtext("pubDate") or "").strip()
                if title and link.startswith("https://"):
                    found.append({"title": title, "url": link, "published": date})
        except Exception as e:
            print("RSS暂不可用:",feed,repr(e))
    return found[:15]
def request_completion(instructions, historical, headlines):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("缺少 OPENAI_API_KEY。请在 GitHub 仓库 Secrets 中配置；不要写入公开文件。")
    prompt = f"""今天北京时间日期：{DATE}。
为私人中文日历杂志创作独立完整的一期十二栏目。输出严格JSON对象：
{{"title":"VOL.XXX｜中文当期标题","items":[{{"title":"01｜栏目标题","body":"至少180字的中文正文；含核心事实、操作方法/分析和必要的真实来源链接"}} ... 共12项]}}。
按顺序必须包含这12项：{", ".join(COLUMNS)}。
每栏要实质内容，不要空泛建议；设计案例要真实项目、设计逻辑、低成本借鉴和可核实资料链接；科学知识讲机制；工具栏提供准确公式和可直接复制使用的短Python脚本或Excel公式（不能虚构已上传文件）；历史真实文物附出处；开源工具附官方链接和使用方法；配色提供5个HEX、加总为100%的比例、材质搭配；思维挑战先解释上期题目（若有）并另出新题，只公布上期答案；电影不剧透；南京植物说明季相、适应性、施工养护；辩论双方论点实质；物件设计含明确尺寸材料加工和风险；第12栏仅采用下列外部RSS真实标题和对应原网址，严格注明实际来源日期，如果不足3条符合当天日期则明确写『本日核验不足3条』，不可假称都是今日新闻、不可编造、不可改写日期；提供最多3条。
最近刊物要避开重复：
{historical}
此次获取的RSS标题及发布日期（仅作为线索；RSS可能不是今天的文章，勿声称已逐篇核实）：
{json.dumps(headlines,ensure_ascii=False)}
注意：不允许编造已生成文件、已运行程序、已验证外部新闻。没有可靠来源时写清无法独立核实。JSON中的字符串须合法，禁止Markdown代码围栏。
"""
    body = {"model":os.environ.get("OPENAI_MODEL","gpt-4.1-mini"),
            "messages":[{"role":"system","content":"你是审慎的中文设计科学杂志编辑。必须输出符合JSON规范的对象，不得编造来源或无依据事实；不能证明的内容标记待核验。"},{"role":"user","content":prompt}],
            "response_format":{"type":"json_object"},
            "temperature":0.7,
            "max_completion_tokens":9500}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=180) as r:
        obj=json.load(r)
    return json.loads(obj["choices"][0]["message"]["content"])
def main():
    data=json.loads(TARGET.read_text(encoding="utf-8")) if TARGET.exists() else {}
    if DATE in data:
        print("已存在本期，不覆盖:", DATE)
        return
    recent = list(data.items())[-4:]
    context = [{"date":d,"title":v.get("title"),"column_titles":[i["title"] for i in v.get("items",[])]} for d,v in recent]
    headlines = news()
    result = request_completion("generate",json.dumps(context,ensure_ascii=False),headlines)
    items=result.get("items",[])
    if len(items)!=12 or any(not isinstance(i,dict) or not isinstance(i.get("title"),str) or not isinstance(i.get("body"),str) or len(i["body"])<90 for i in items):
        raise ValueError("AI输出未通过完整12栏和正文校验，本期不发布，避免出现缺栏目。")
    if not all(re.match(rf"0?{idx}[｜.、 ]",i["title"]) for idx,i in enumerate(items,1)):
        raise ValueError("栏目编号缺失或顺序不正确")
    data[DATE]={"title":result.get("title","十二维｜"+DATE),"items":items}
    TARGET.write_text(json.dumps(dict(sorted(data.items())),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("发布完成",DATE,"12栏，总正文",sum(len(i["body"]) for i in items),"字")
if __name__=="__main__":
    main()
