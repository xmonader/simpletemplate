from simpletemplate import *


def test1():
    tmpl = """hello %%= name %%"""
    out = parse_html(tmpl, {'name': 'ahmed'})
    print(out)


def test2():
    tmpl = """ hello %%= firstname %% %%= lastname %% whatss up?"""
    out = parse_html(tmpl, {'firstname': 'ahmed', 'lastname': 'striky'})
    print(out)


def test3():
    tmpl = """
    hello %%= name %%
    %% if 3 5 < %%
    <h1>3 is less than 5</h1>
    %% endif %%
    """
    out = parse_html(tmpl, {'name': 'ahmed', 'x': 99})
    print(out)


def test4():
    tmpl = """
    hello %%= name %%
    %% for lang in langs %%
    <h1>%%= lang %%</h1>
    %% endfor %%
    """
    out = parse_html(
        tmpl, {'name': 'ahmed', 'langs': ['py', 'ruby', 'java']})
    print(out)


def test5():
    tmpl = """
    hello %%= name %%
    %% for lang in langs %%
    <h1> %%= lang %% </h1>
    %% endfor %%
    %% for num in nums_list %%
    %% if num 30 < %%
        <h1>  \u001b[4%%= loopidx %%m << \u001b[0m %%= num %% is less than 30</h1>
    %% endif %%
    %% endfor %%
    """
    out = parse_html(tmpl, {'name': 'ahmed', 'langs': [
                          'py', 'ruby', 'java'], 'nums_list': range(10)})
    print(out)


def test6():
    tmpl = """
    hello %%= name %%
    %% for x in xs %%
    %% if x 5 < %%
    <h1> %%= x %% is less than 5</h1>
    %% endif %%
    %% endfor %%
    """
    out = parse_html(tmpl, {'name': 'ahmed', 'x': 99, 'xs': [3, 2, 1]})
    print(out)


if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    test5()
    # test6()
