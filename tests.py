from simpletemplate import *


def test1():
    tmpl = """hello %% {{name}} %%"""
    root = parse_template(tmpl, {'name': 'ahmed'})
    print(root.render())


def test2():
    tmpl = """ hello %% {{firstname}} %% %% {{lastname}} %% whatss up?"""
    root = parse_template(tmpl, {'firstname': 'ahmed', 'lastname': 'striky'})
    print(root.render())


def test3():
    tmpl = """
    hello %% {{name}} %%
    %% if 3 5 < %%
    <h1>3 is less than 5</h1>
    %% endif %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'x': 99})
    print(root.render())


def test4():
    tmpl = """
    hello %% {{name}} %%
    %% for lang in langs %%
    <h1>%% {{lang}} %%</h1>
    %% endfor %%
    """
    root = parse_template(
        tmpl, {'name': 'ahmed', 'langs': ['py', 'ruby', 'java']})
    print(root.render())


def test5():
    tmpl = """
    hello %% {{name}} %%
    %% for lang in langs %%
    <h1> %% {{lang}} %% </h1>
    %% endfor %%
    %% for num in nums_list %%
    %% if 4 5 == %%
        <h1> has 5 in</h1>
    %% endif %%
    <h1>%% {{num}} %%</h1>
    %% endfor %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'langs': [
                          'py', 'ruby', 'java'], 'nums_list': [241, 24, 11]})
    print(root.render())


def test6():
    tmpl = """
    hello %% {{name}} %%
    %% for x in xs %%
    %% if x 5 < %%
    <h1> %% {{x}} %% is less than 5</h1>
    %% endif %%
    %% endfor %%
    """
    root = parse_template(tmpl, {'name': 'ahmed', 'x': 99, 'xs': [3, 2, 1]})
    print(root.render())


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
