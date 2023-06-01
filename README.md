# newick-tree-builder

**A small, stand-alone**\* **library for making trees in [New Hampshire notation (also known as Newick format)](https://en.wikipedia.org/wiki/Newick_format).**

For releases, see [PyPI](https://pypi.org/project/newick-tree-builder/).

_Note that this library is basically just a notation converter. It does not visualize the trees and it has no CLI built-in. It consists of a parser front-end and, mostly, a backend providing the newick tree data structure._

This package is also on PyPI, btw.

### Backend: The Data Structure

The main part is the **backend**, which is intended to provide a very flexible data structure for representation of Newick trees. 
Besides basic newick tree functionality, it provides some advanced features, such as:
  * Built-in **dynamic** (and freely defineable, though fiddly) **adjustment of distances** of nodes from their parents on duplication (with *average* as built-in default)
  * Automatic, built-in **duplication counting**
  * **New Hampshire X** compliant attachment of additional data to each node via Python `dict`s; with `list`s and `set`s merging automatically on duplication
  * Highly customizable Newick string generation, including
    * function-based **customizable labelling** of nodes in the output, independent from their actual label in the data structure
    * individual switches for outputting labels, distances and attached additional info (NH-X)
  * **Hybridisation** (Extended Newick), although that is severely under-tested and not supported yet by the currently implemented `very_basic` parser

### Frontend: Parsing

That part is mostly left as an exercise for the reader. 

Currently there is only a very ugly `very_basic` parser implemented, which supports inputs via `Path`s (sequences of pairs of a label and a distance each), e.g.:
    ```
    A:1,B:2,D,E:4;
    A,B,F:2,G:1,D;
    ```
with nodes A, B, C, D, E, F, G. Note that the two D nodes here are not the same, they are completely seperate instances. The numbers after the colons after each node label represent the distances of the node. They are optional. 
The semicolon marks the end of a path.

The `very_basic` parser supports:
  * Choosing the label of the automatically created root node
  * Labels and distances -- input as a string of paths as laid out in the example above
  * Customizable delimiters and white-spaces
  * Blacklisted labels, as well as four pre-defined policies of dealing with them
  * Passing a distance adjustment function on duplication 

More parsers are planned, but I'd recomment to build your own. 

## A Practical Example

### Using the `very_basic` Parser

Let's say we have a table of item, categorized to corresponding taxa of the species they balong to -- we don't care what this is or where it came from, but it looks something like this:

```
    Heunggongvirae,Uroviricota,Caudoviricetes,Caudovirales,O,O,O;
    n.a.,n.a.,n.a.,n.a.,n.a.,n.a.,n.a.;
    Heunggongvirae,Uroviricota,Caudoviricetes,Caudovirales,Demerecviridae,Ermolyevavirinae,Unclassified;
```

For simplicity, we assign no distance to each waypoint of each path through the tree. The data structure will automatically assign a default distance.
Then this is already a format the `very_basic` parser can understand. Let's say the variable `text` already contains the text above. 
Then we can do:

```python
    from newick.frontend.very_basic import tree_parse_basic
    
    t = tree_parse_basic(txt, "root")
    print(t.to_string())
    
    #> (((((O:1,((Unclassified:1)Ermolyevavirinae:1)Demerecviridae:1)Caudovirales:1)Caudoviricetes:1)Uroviricota:1)Heunggongvirae:1,n.a.:1)root;
```

If you already have a bit of practice reading newick format, you might wonder where all the "n.a." nodes have gone. The parser has removed them, because "n.a." is blacklisted by default and the default strategy is DROP_AFTER_FIRST, leaving the first "n.a." in the path, but ignoring all its children.
If we don't want this behaviour and also no distances, we can do:

```python
    from newick.frontend.very_basic import tree_parse_basic, BlacklistTokenStrat
    
    t = tree_parse_basic(txt, "root", blacklist_token_strat=BlacklistTokenStrat.IGNORE_BLACKLIST)
    print(t.to_string())
    
    #> (((((((O)O)O,((Unclassified)Ermolyevavirinae)Demerecviridae)Caudovirales)Caudoviricetes)Uroviricota)Heunggongvirae,((((((n.a.)n.a.)n.a.)n.a.)n.a.)n.a.)n.a.)r;
```

and voila, we get the whole "n.a." branch in the output. ("O" is also blacklisted by default, so that branch was extended as well.)

### Using the `Tree` Data Structure

Instead of building a whole parser here, let's just fool around a bit and build a few Trees by hand. 

We start by importing some stuff and creating a Tree object. Note that the `Tree` class forwards the constructors for `Path` and `RootNode`, so that you won't have all the import clutter in your program. 

```python
    from newick.backend.tree import Tree

    t = Tree.RootNode("R")
    print(t.to_string())
    
    #> R;
```

Now let's add a child to that root node by defining their `Path`s and then adding them using the `Tree`:

```python
    path_A = Tree.Path("R", [("A", 1.0)])
    t.add_new_node(path_A)
```

The `Path` is created by passing to it the label of the root node, "R", and a `list` of waypoints, which are tuples of a label (`str`) and a distance (`float`) each. In this case, there is only one waypoint besides the root: "A" at a distance of `1.0` from its parent. This list can contain any number of waypoints as we will see, except 0. 
Let's have a look at the result:

```python
    print(t.to_string())
    
    #> (A:1)R;
```

Let's add another node to it:

```python
    t.add_new_node(Tree.Path("R", [("A", float("-inf")), ("B", 2.0)]))
    print(t.to_string())
    
    #> ((B:2)A:1)R;
```

The distance of `float("-inf")` signals `t` that this waypoint has no distance assigned, meaning for a new node assign the default distance, and for an existing node to not adjust the distance.
Let's say we have a duplicate of "A", with a different distance, so we now want it to update. The default distance adjustment strategy is to set it to the average of all distances, but other pre-defined strategies can be found in the `Tree` class and, of course, be defined by the user. We will stick to the default for now.

```python
    t.add_new_node(Tree.Path("R", [("A", 3.0)]))
    print(t.to_string())
    
    #> ((B:2)A:2)R;
```

The distance of "A" has been changed to the average of 1 and 3, which is 2. 
Now let's branch out and create some more leaves.

```python
    t.add_new_node(Tree.Path("R", [("X", 4.0), ("Y", 3.0), ("Z", float("-inf"))]))
    print(t.to_string())
    
    #> ((B:2)A:2,((Z:1)Y:3)X:4)R;
```

If we wanted to see this tree without distances, labels or both, we can print it like that without having to re-build it:

```python
    print(t.to_string(with_distances=False))
    print(t.to_string(with_labels=False))
    print(t.to_string(with_distances=False, with_labels=False))
    
    #> ((B)A,((Z)Y)X)R;
    #> ((:2):2,((:1):3):4);
    #> ((),(()));
```

Now let's assume we want only leaves to print labels. That can be achieved using a custom label mapping function. Such functions map a node to its to-be-printed (fake-)label string. For example:

```python
    only_leaves_name_mapper = \
        lambda node: node.get_label() if node.is_leaf() else ""
    print(t.to_string(outputlabel_mapper=only_leaves_name_mapper))
    
    #> ((B:2):2,((Z:1):3):4);
```

Beautiful!

There are many more features and even more possible combinations of configurations, but let's wrap this up for now with a word about custom parsers: I'd recomment You mostly rely on the `Tree`'s functionality when it comes to building your own parser, and not manipulate nodes directly. You can certainly do wild things with overriding some `Node` methods and having custom node types, but please do so with care as many built-in features will probably break in the process. For example, the _DIST_ADJUST_STRAT_AVERAGE, which is the default, relies on duplicate counting, which is implemented in the `handle_duplicate` function of a `Node`. Such couplings are not obvious, and bear a massive risk of causing mayham and really awful bugs that will be terrible to hunt down for You. So do yourself a favor and try to stick with the built-in nodes, or modify them directly in a custom branch of this library. 

## License

This project is published under the CC0 license, so it is basically Public Domain. 
Feel free to contribute, fork, copy, steal, shoot to the moon or burn.

To the students of you: Please notice that that does not free you from having to cite this code if you choose use it. 


----

\* New parsers may bring dependencies with them in the future.
