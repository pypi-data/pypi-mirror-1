#------------------------------------------------------------------------------
#  Copyright (c) 2009 Richard W. Lincoln
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#------------------------------------------------------------------------------

""" Defines a representation of a graph in Graphviz's dot language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
import subprocess
import tempfile
import math
import logging

from enthought.traits.api import \
    HasTraits, Any, Instance, Trait, Tuple, Bool, Str, Enum, Float, Color, \
    Either, Range, Int, Font, List, Directory, ListInstance, This, Property, \
    Dict, on_trait_change

from enthought.traits.trait_handlers import TraitListEvent

from enthought.traits.ui.api import View, Group, Item, Tabbed
from enthought.pyface.image_resource import ImageResource
from enthought.enable.api import Canvas, Viewport, Container
from enthought.enable.tools.api import ViewportPanTool, ViewportZoomTool
from enthought.enable.component_editor import ComponentEditor

from common import \
    Alias, color_scheme_trait, rectangle_trait, fontcolor_trait, \
    fontname_trait, fontsize_trait, label_trait, point_trait, pointf_trait, \
    nojustify_trait, root_trait, showboxes_trait, target_trait, margin_trait

from godot.base_graph import BaseGraph
from godot.node import Node
from godot.edge import Edge
from godot.subgraph import Subgraph
from godot.cluster import Cluster

from godot.ui.graph_view import graph_view, tabbed_view

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

cluster_mode_trait = Enum(
    "local", "global", "none", desc="mode used for handling clusters",
    label="Cluster rank", graphviz=True
)

start_trait = Enum("regular", "self", "random", graphviz=True)

#------------------------------------------------------------------------------
#  "Graph" class:
#------------------------------------------------------------------------------

class Graph(BaseGraph):
    """ Defines a representation of a graph in Graphviz's dot language.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions.
    #--------------------------------------------------------------------------

    # A strict graph is an unweighted, undirected graph containing no
  # graph loops or multiple edges.
    strict = Bool(False, desc="A strict graph is an unweighted, "
        "undirected graph containing no graph loops or multiple edges." )

    # Do edges have direction?
    directed = Bool(False, desc="directed edges.")

    # All graphs, subgraphs and clusters.
    all_graphs = Property( List(Instance(BaseGraph)) )

    #--------------------------------------------------------------------------
    #  Dot trait definitions.
    #--------------------------------------------------------------------------

    # Bounding box of drawing in integer points.
    bb = rectangle_trait

    # When attached to the root graph, this color is used as the background for
    # entire canvas. When a cluster attribute, it is used as the initial
    # background for the cluster. If a cluster has a filled
    # <html:a rel="attr">style</html:a>, the
    # cluster's <html:a rel="attr">fillcolor</html:a> will overlay the
    # background color.
    #
    # If no background color is specified for the root graph, no graphics
    # operation are performed on the background. This works fine for
    # PostScript but for bitmap output, all bits are initialized to something.
    # This means that when the bitmap output is included in some other
    # document, all of the bits within the bitmap's bounding box will be
    # set, overwriting whatever color or graphics where already on the page.
    # If this effect is not desired, and you only want to set bits explicitly
    # assigned in drawing the graph, set <html:a rel="attr">bgcolor</html:a>="transparent".
    bgcolor = Color("white", desc="color used as the background for the "
        "entire canvas", label="Background Color", graphviz=True)

  # If true, the drawing is centered in the output canvas.
    center = Bool(False, desc="is drawing centered in the output canvas",
        graphviz=True)

    # Specifies the character encoding used when interpreting string input
    # as a text label. The default value is <html:span class="val">UTF-8</html:span>.
    # The other legal value is <html:span class="val">iso-8859-1</html:span> or,
    # equivalently,
    # <html:span class="val">Latin1</html:span>. The <html:a rel="attr">charset</html:a> attribute is case-insensitive.
    # Note that if the character encoding used in the input does not
    # match the <html:a rel="attr">charset</html:a> value, the resulting output may be very strange.
    charset = Str("UTF-8", label="Character encoding", graphviz=True)

    # Mode used for handling clusters. If <html:a rel="attr">clusterrank</html:a> is <html:span class="val">local</html:span>, a
    # subgraph whose name begins with "cluster" is given special treatment.
    # The subgraph is laid out separately, and then integrated as a unit into
    # its parent graph, with a bounding rectangle drawn about it.
    # If the cluster has a <html:a rel="attr">label</html:a> parameter, this label
    # is displayed within the rectangle.
    # Note also that there can be clusters within clusters.
    # At present, the modes <html:span class="val">global</html:span> and <html:span class="val">none</html:span>
    # appear to be identical, both turning off the special cluster processing.
    clusterrank = cluster_mode_trait

    # This attribute specifies a color scheme namespace. If defined, it specifies
    # the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = color_scheme_trait

  # Comments are inserted into output. Device-dependent.
    comment = Str(desc="comments are inserted into output", graphviz=True)

  # If <html:span class="val">true</html:span>, allow edges between clusters.
    # (See <html:a rel="attr">lhead</html:a> and <html:a rel="attr">ltail</html:a> below.)
    compound = Bool(False, desc="edges allowed between clusters",
        graphviz=True)

  # If <html:span class="val">true</html:span>, use edge concentrators.
    concentrate = Bool(False, desc="edge concentrators", graphviz=True)

    # Factor damping force motions. On each iteration, a nodes movement
    # is limited to this factor of its potential motion. By being less than
    # 1.0, the system tends to "cool", thereby preventing cycling.
    Damping = Float(0.99, desc="factor damping force motions", graphviz=True)

    # This specifies the distance between nodes in separate connected
    # components. If set too small, connected components may overlap.
    # Only applicable if <html:a rel="attr">pack</html:a>=false.
    defaultdist = Float(desc="distance between nodes in separate connected "
        "components", label="Default distance", graphviz=True)

    # Set the number of dimensions used for the layout. The maximum value
    # allowed is 10.
    dim = Range(low=2, high=10, desc="number of dimensions for the layout",
        label="Dimensions", graphviz=True)

    # Only valid when mode="ipsep". If true, constraints are generated for each
    # edge in the largest (heuristic) directed acyclic subgraph such that the
    # edge must point downwards. If "hier", generates level constraints similar
    # to those used with mode="hier". The main difference is that, in the
    # latter case, only these constraints are involved, so a faster solver can
    # be used.
    diredgeconstraints = Enum(True, "heir", label="Edge constraints",
        graphviz=True)

    # This specifies the expected number of pixels per inch on a display device.
    # For bitmap output, this guarantees that text rendering will be
    # done more accurately, both in size and in placement. For SVG output,
    # it is used to guarantee that the dimensions in the output correspond to
    # the correct number of points or inches.
    dpi = Float(96.0, desc="expected number of pixels per inch on a display",
        label="DPI", graphviz=True)

    # Terminating condition. If the length squared of all energy gradients are
    # &lt; <html:a rel="attr">epsilon</html:a>, the algorithm stops.
    epsilon = Float(0.0001, desc="terminating condition", graphviz=True)

    # Fraction to increase polygons (multiply
    # coordinates by 1 + esep) for purposes of spline edge routing.
    # This should normally be strictly less than
    # <html:a rel="attr">sep</html:a>.
    esep = Int(3, desc="Fraction to increase polygons (multiply coordinates "
        "by 1 + esep) for purposes of spline edge routing",
        label="Edge separation", graphviz=True)

  # Color used for text.
    fontcolor = fontcolor_trait

    # Font used for text. This very much depends on the output format and, for
    # non-bitmap output such as PostScript or SVG, the availability of the font
    # when the graph is displayed or printed. As such, it is best to rely on
    # font faces that are generally available, such as Times-Roman, Helvetica or
    # Courier.
    #
    # If Graphviz was built using the
    # <html:a href="http://pdx.freedesktop.org/~fontconfig/fontconfig-user.html">fontconfig library</html:a>, the latter library
    # will be used to search for the font. However, if the <html:a rel="attr">fontname</html:a> string
    # contains a slash character "/", it is treated as a pathname for the font
    # file, though font lookup will append the usual font suffixes.
    #
    # If Graphviz does not use fontconfig, <html:a rel="attr">fontname</html:a> will be
    # considered the name of a Type 1 or True Type font file.
    # If you specify <html:code>fontname=schlbk</html:code>, the tool will look for a
    # file named  <html:code>schlbk.ttf</html:code> or <html:code>schlbk.pfa</html:code> or <html:code>schlbk.pfb</html:code>
    # in one of the directories specified by
    # the <html:a rel="attr">fontpath</html:a> attribute.
    # The lookup does support various aliases for the common fonts.
    fontname = fontname_trait

    # Allows user control of how basic fontnames are represented in SVG output.
    # If <html:a rel="attr">fontnames</html:a> is undefined or <html:span class="val">svg</html:span>,
    # the output will try to use known SVG fontnames. For example, the
    # default font <html:code>Times-Roman</html:code> will be mapped to the
    # basic SVG font <html:code>serif</html:code>. This can be overridden by setting
    # <html:a rel="attr">fontnames</html:a> to <html:span class="val">ps</html:span> or <html:span class="val">gd</html:span>.
    # In the former case, known PostScript font names such as
    # <html:code>Times-Roman</html:code> will be used in the output.
    # In the latter case, the fontconfig font conventions
    # are used. Thus, <html:code>Times-Roman</html:code> would be treated as
    # <html:code>Nimbus Roman No9 L</html:code>. These last two options are useful
    # with SVG viewers that support these richer fontname spaces.
    fontnames = Enum("svg", "ps", "gd", label="Font names",
        desc="how basic fontnames are represented in SVG output",
        graphviz=True)

    # Directory list used by libgd to search for bitmap fonts if Graphviz
    # was not built with the fontconfig library.
    # If <html:a rel="attr">fontpath</html:a> is not set, the environment
    # variable <html:code>DOTFONTPATH</html:code> is checked.
    # If that is not set, <html:code>GDFONTPATH</html:code> is checked.
    # If not set, libgd uses its compiled-in font path.
    # Note that fontpath is an attribute of the root graph.
    fontpath = List(Directory, label="Font path", graphviz=True)

  # Font size, in <html:a rel="note">points</html:a>, used for text.
    fontsize = fontsize_trait

    # Spring constant used in virtual physical model. It roughly corresponds to
    # an ideal edge length (in inches), in that increasing K tends to increase
    # the distance between nodes. Note that the edge attribute len can be used
    # to override this value for adjacent nodes.
    K = Float(0.3, desc="spring constant used in virtual physical model",
        graphviz=True)

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = label_trait

    # Justification for cluster labels. If <html:span class="val">r</html:span>, the label
    # is right-justified within bounding rectangle; if <html:span class="val">l</html:span>, left-justified;
    # else the label is centered.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labeljust</html:a> to <html:span class="val">l</html:span>, the subgraph inherits
    # this value.
    labeljust = Trait("c", {"Centre": "c", "Right": "r", "Left": "l"},
        desc="justification for cluster labels", label="Label justification",
        graphviz=True)

    # Top/bottom placement of graph and cluster labels.
    # If the attribute is <html:span class="val">t</html:span>, place label at the top;
    # if the attribute is <html:span class="val">b</html:span>, place label at the bottom.
    # By default, root
    # graph labels go on the bottom and cluster labels go on the top.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labelloc</html:a> to <html:span class="val">b</html:span>, the subgraph inherits
    # this value.
    labelloc = Trait("b", {"Bottom": "b", "Top":"t"},
        desc="placement of graph and cluster labels",
        label="Label location", graphviz=True)

    # If true, the graph is rendered in landscape mode. Synonymous with
    # <html:code><html:a rel="attr">rotate</html:a>=90</html:code> or <html:code>
    # <html:a rel="attr">orientation</html:a>=landscape</html:code>.
    landscape = Bool(False, desc="rendering in landscape mode", graphviz=True)

    # Specifies a linearly ordered list of layer names attached to the graph
    # The graph is then output in separate layers. Only those components
    # belonging to the current output layer appear. For more information,
    # see the page <html:a href="http://www.graphviz.org/Documentation/html/layers/">How to use drawing layers (overlays)</html:a>.
    layers = Str(desc="a linearly ordered list of layer names",
        graphviz=True)

    # Specifies the separator characters used to split the
    # <html:a rel="attr">layers </html:a>attribute into a list of layer names.
    layersep = Enum(":\t", "\t", " ", label="Layer separation",
        desc="separator characters used to split layer names", graphviz=True)

    # Specifies strictness of level constraints in neato
    # when <html:code><html:a rel="attr">mode</html:a>="ipsep" or "hier"</html:code>.
    # Larger positive values mean stricter constraints, which demand more
    # separation between levels. On the other hand, negative values will relax
    # the constraints by allowing some overlap between the levels.
    levelsgap = Float(0.0, desc="strictness of level constraints in neato",
        label="Levels gap", graphviz=True)

    # Label position, in points. The position indicates the center of the
    # label.
    lp = point_trait

    # For graphs, this sets x and y margins of canvas, in inches. If the margin
    # is a single double, both margins are set equal to the given value.
    #
    # Note that the margin is not part of the drawing but just empty space
    # left around the drawing. It basically corresponds to a translation of
    # drawing, as would be necessary to center a drawing on a page. Nothing
    # is actually drawn in the margin. To actually extend the background of
    # a drawing, see the <html:a rel="attr">pad</html:a> attribute.
    #
    # For nodes, this attribute specifies space left around the node's label.
    # By default, the value is <html:code>0.11,0.055</html:code>.
    margin = margin_trait#Either(Float, pointf_trait, desc="x and y margins of canvas")

    # Sets the number of iterations used.
    maxiter = Int(200, desc="number of iterations used",
        label="Maximum iterations", graphviz=True)

    # Multiplicative scale factor used to alter the MinQuit (default = 8)
    # and MaxIter (default = 24) parameters used during crossing
    # minimization. These correspond to the
    # number of tries without improvement before quitting and the
    # maximum number of iterations in each pass.
    mclimit = Float(1.0, desc="Multiplicative scale factor used to alter the "
        "MinQuit (default = 8) and MaxIter (default = 24) parameters used "
        "during crossing minimization", label="Multiplicative scale factor",
        graphviz=True)

  # Specifies the minimum separation between all nodes.
    mindist = Float(1.0, desc="minimum separation between all nodes",
        label="Minimum separation", graphviz=True)

    # Technique for optimizing the layout. If <html:a rel="attr">mode</html:a> is <html:span class="val">major</html:span>,
    # neato uses stress majorization. If <html:a rel="attr">mode</html:a> is <html:span class="val">KK</html:span>,
    # neato uses a version of the gradient descent method. The only advantage
    # to the latter technique is that it is sometimes appreciably faster for
    # small (number of nodes &lt; 100) graphs. A significant disadvantage is that
    # it may cycle.
    #
    # There are two new, experimental modes in neato, <html:span class="val">hier</html:span>, which adds a top-down
    # directionality similar to the layout used in dot, and <html:span class="val">ipsep</html:span>, which
    # allows the graph to specify minimum vertical and horizontal distances
    # between nodes. (See the <html:a rel="attr">sep</html:a> attribute.)
    mode = Enum("major", "KK", "heir", "ipsep",
        desc="Technique for optimizing the layout", graphviz=True)

    # This value specifies how the distance matrix is computed for the input
    # graph. The distance matrix specifies the ideal distance between every
    # pair of nodes. neato attemps to find a layout which best achieves
    # these distances. By default, it uses the length of the shortest path,
    # where the length of each edge is given by its <html:a rel="attr">len</html:a>
    # attribute. If <html:a rel="attr">model</html:a> is <html:span class="val">circuit</html:span>, neato uses the
    # circuit resistance
    # model to compute the distances. This tends to emphasize clusters. If
    # <html:a rel="attr">model</html:a> is <html:span class="val">subset</html:span>, neato uses the subset model. This sets the
    # edge length to be the number of nodes that are neighbors of exactly one
    # of the end points, and then calculates the shortest paths. This helps
    # to separate nodes with high degree.
    model = Enum("shortpath", "circuit", "subset",
        desc="how the distance matrix is computed for the input graph",
        graphviz=True)

    # If Graphviz is built with MOSEK defined, mode=ipsep and mosek=true,
    # the Mosek software (www.mosek.com) is use to solve the ipsep constraints.
    mosek = Bool(False, desc="solve the ipsep constraints with MOSEK",
        graphviz=True)

  # Minimum space between two adjacent nodes in the same rank, in inches.
    nodesep = Float(0.25, desc="minimum space between two adjacent nodes in "
        "the same rank", label="Node separation", graphviz=True)

    # By default, the justification of multi-line labels is done within the
    # largest context that makes sense. Thus, in the label of a polygonal node,
    # a left-justified line will align with the left side of the node (shifted
    # by the prescribed margin). In record nodes, left-justified line will line
    # up with the left side of the enclosing column of fields. If nojustify is
    # "true", multi-line labels will be justified in the context of itself. For
    # example, if the attribute is set, the first label line is long, and the
    # second is shorter and left-justified, the second will align with the
    # left-most character in the first line, regardless of how large the node
    # might be.
    nojustify = nojustify_trait

    # If set, normalize coordinates of final
    # layout so that the first point is at the origin, and then rotate the
    # layout so that the first edge is horizontal.
    normalize = Bool(False, desc="If set, normalize coordinates of final "
        "layout so that the first point is at the origin, and then rotate the "
        "layout so that the first edge is horizontal", graphviz=True)

    # Used to set number of iterations in
    # network simplex applications, used in
    # computing node x coordinates.
    # If defined, # iterations =  <html:a rel="attr">nslimit</html:a> * # nodes;
    # otherwise,  # iterations = MAXINT.
    nslimit = Float(desc="iterations in network simplex applications",
        label="x-coordinate limit", graphviz=True)

    # Used to set number of iterations in
    # network simplex applications, used for ranking nodes.
    # If defined, # iterations =  <html:a rel="attr">nslimit1</html:a> * # nodes;
    # otherwise,  # iterations = MAXINT.
    nslimit1 = Float(desc="iterations in network simplex applications",
        label="Ranking limit", graphviz=True)

    # If "out" for a graph G, and n is a node in G, then edges n-&gt;* appear
    # left-to-right in the same order in which they are defined.
    # If "in", the edges *-&gt;n appear
    # left-to-right in the same order in which they are defined for all
    # nodes n.
    ordering = Enum("out", "in", desc="If 'out' for a graph G, and n is a "
        "node in G, then edges n->* appear left-to-right in the same order in "
        "which they are defined. If 'in', the edges *->n appear left-to-right "
        "in the same order in which they are defined for all nodes n.",
        graphviz=True)

    # These specify the order in which nodes and edges are drawn in concrete
    # output. The default "breadthfirst" is the simplest, but when the graph
    # layout does not avoid edge-node overlap, this mode will sometimes have
    # edges drawn over nodes and sometimes on top of nodes. If the mode
    # "nodesfirst" is chosen, all nodes are drawn first, followed by the
    # edges. This guarantees an edge-node overlap will not be mistaken for
    # an edge ending at a node. On the other hand, usually for aesthetic
    # reasons, it may be desirable that all edges appear beneath nodes,
    # even if the resulting drawing is ambiguous. This can be achieved by
    # choosing "edgesfirst".
    outputorder = Enum("breadthfirst", "nodesfirst", "edgesfirst",
        desc="order in which nodes and edges are drawn", label="Output order",
        graphviz=True)

    # Determines if and how node overlaps should be removed. Nodes are first
    # enlarged using the <html:a rel="attr">sep</html:a> attribute.
    # If <html:span class="val">true</html:span>, overlaps are retained.
    # If the value is <html:span class="val">scale</html:span>, overlaps are removed by uniformly scaling in x and y.
    # If the value converts to <html:span class="val">false</html:span>, node overlaps are removed by a
    # Voronoi-based technique.
    # If the value is <html:span class="val">scalexy</html:span>, x and y are separately
    # scaled to remove overlaps.
    # If the value is <html:span class="val">orthoxy</html:span> or <html:span class="val">orthoyx</html:span>, overlaps
    # are moved by optimizing two constraint problems, one for the x axis and
    # one for the y. The suffix indicates which axis is processed first.
    # If the value is <html:span class="val">ortho</html:span>, the technique is similar to <html:span class="val">orthoxy</html:span> except a
    # heuristic is used to reduce the bias between the two passes.
    # If the value is <html:span class="val">ortho_yx</html:span>, the technique is the same as <html:span class="val">ortho</html:span>, except
    # the roles of x and y are reversed.
    # The values <html:span class="val">portho</html:span>, <html:span class="val">porthoxy</html:span>, <html:span class="val">porthoxy</html:span>, and <html:span class="val">portho_yx</html:span> are similar
    # to the previous four, except only pseudo-orthogonal ordering is
    # enforced.
    #
    # If the value is <html:span class="val">compress</html:span>, the layout will be scaled down as much as
    # possible without introducing any overlaps, obviously assuming there are
    # none to begin with.
    #
    # If the value is <html:span class="val">ipsep</html:span>, and the layout is done by neato with
    # <html:a rel="attr">mode</html:a>="ipsep", the overlap removal constraints are
    # incorporated into the layout algorithm itself.
    # N.B. At present, this only supports one level of clustering.
    #
    # If the value is <html:span class="val">vpsc</html:span>, overlap removal is similarly to <html:span class="val">ortho</html:span>, except
    # quadratic optimization is used to minimize node displacement.
    # N.B. At present, this mode only works when <html:a rel="attr">mode</html:a>="ipsep".
    #
    # Except for fdp, the layouts assume <html:code>overlap="true"</html:code> as the default.
    # Fdp first uses a number of passes using built-in, force-directed technique
    # to remove overlaps. Thus, fdp accepts <html:a rel="attr">overlap</html:a> with an integer
    # prefix followed by a colon, specifying the number of tries. If there is
    # no prefix, no initial tries will be performed. If there is nothing following
    # a colon, none of the above methods will be attempted. By default, fdp
    # uses <html:code>overlap="9:portho"</html:code>. Note that <html:code>overlap="true"</html:code>,
    # <html:code>overlap="0:true"</html:code> and <html:code>overlap="0:"</html:code> all turn off all overlap
    # removal.
    #
    # Except for the Voronoi method, all of these transforms preserve the
    # orthogonal ordering of the original layout. That is, if the x coordinates
    # of two nodes are originally the same, they will remain the same, and if
    # the x coordinate of one node is originally less than the x coordinate of
    # another, this relation will still hold in the transformed layout. The
    # similar properties hold for the y coordinates.
    # This is not quite true for the "porth*" cases. For these, orthogonal
    # ordering is only preserved among nodes related by an edge.
    #
    # <html:b>NOTE</html:b>The methods <html:span class="val">orthoxy</html:span> and <html:span class="val">orthoyx</html:span> are still evolving. The semantics of these may change, or these methods may disappear altogether.
    overlap = Enum("True", "False", "scale", "scalexy", "prism", "compress",
        "vpsc", "ipsep", desc="determines if and how node overlaps should be "
        "removed", graphviz=True)

    # This is true if the value of pack is "true" or a non-negative integer.
    # If true, each connected component of the graph is laid out separately,
    # and then the graphs are packed tightly. If pack has an integral value,
    # this is used as the size, in points, of a margin around each part;
    # otherwise, a default margin of 8 is used. If pack is interpreted as
    # false, the entire graph is laid out together. The granularity and method
    # of packing is influenced by the packmode attribute.
    #
    # For layouts which always do packing, such a twopi, the pack attribute is
    # just used to set the margin.
    pack = Bool(graphviz=True) #Either(
#        Bool, Int, desc="If true, each connected component of the graph is "
#        "laid out separately, and then the graphs are packed tightly"
#    )

    # This indicates the granularity and method used for packing
    # (cf. <html:a rel="type">packMode</html:a>). Note that defining
    # <html:a rel="attr">packmode</html:a> will automatically turn on packing as though one had
    # set <html:code>pack=true</html:code>.
    #
    # "node","clust","graph" These specify the granularity of packing connected
    # components when the pack attribute is true. A value of "node" causes
    # packing at the node and edge label, with no overlapping of these objects.
    # This produces a layout with the least area, but it also allows
    # interleaving, where a node of one component may lie between two nodes in
    # another component. A value of "graph" does a packing using the bounding
    # box of the component. Thus, there will be a rectangular region around a
    # component free of elements of any other component. A value of "clust"
    # guarantees that top-level clusters are kept intact. What effect a value
    # has also depends on the layout algorithm. For example, neato does not
    # support clusters, so a value of "clust" will have the same effect as the
    # default "node" value.
    packmode = Enum("node", "cluster", "graph", label="Pack mode",
        desc="granularity and method used for packing", graphviz=True)

    # The pad attribute specifies how much, in inches, to extend the
    # drawing area around the minimal area needed to draw the graph.
    # If the pad is a single double, both the x and y pad values are set
    # equal to the given value. This area is part of the
    # drawing and will be filled with the background color, if appropriate.
    #
    # Normally, a small pad is used for aesthetic reasons, especially when
    # a background color is used, to avoid having nodes and edges abutting
    # the boundary of the drawn region.
    pad = Float(0.0555, desc="how much to extend the drawing area around the "
        "minimal area needed to draw the graph", graphviz=True)

    # Width and height of output pages, in inches. If this is set and is
    # smaller than the size of the layout, a rectangular array of pages of the
    # specified page size is overlaid on the layout, with origins aligned in
    # the lower-left corner, thereby partitioning the layout into pages. The
    # pages are then produced one at a time, in pagedir order.
    #
    # At present, this only works for PostScript output. For other types of
    # output, one should use another tool to split the output into multiple
    # output files. Or use the viewport to generate multiple files.
    page = pointf_trait

    # If the <html:a rel="attr">page</html:a> attribute is set and applicable,
    # this attribute specifies the order in which the pages are emitted.
    # This is limited to one of the 8 row or column major orders.
    pagedir = Enum("BL", "BR", "TL", "TR", "RB", "RT", "LB", "LT",
        desc="If the page attribute is set and applicable, this attribute "
        "specifies the order in which the pages are emitted",
        label="Page direction", graphviz=True)

    # If <html:a rel="attr">quantum</html:a> &gt; 0.0, node label dimensions
    # will be rounded to integral multiples of the quantum.
    quantum = Float(0.0, desc="If quantum > 0.0, node label dimensions will "
        "be rounded to integral multiples of the quantum.", graphviz=True)

    # Sets direction of graph layout. For example, if <html:a rel="attr">rankdir</html:a>="LR",
    # and barring cycles, an edge <html:code>T -&gt; H;</html:code> will go
    # from left to right. By default, graphs are laid out from top to bottom.
    rankdir = Enum("TB", "LR", "BT", "RL", desc="direction of graph layout",
        label="Rank direction", graphviz=True)

    # In dot, this gives the desired rank separation, in inches. This is
    # the minimum vertical distance between the bottom of the nodes in one
    # rank and the tops of nodes in the next. If the value
    # contains "equally", the centers of all ranks are spaced equally apart.
    # Note that both
    # settings are possible, e.g., ranksep = "1.2 equally".
    # In twopi, specifies radial separation of concentric circles.
    ranksep = Float(0.5, desc="In dot, this gives the desired rank "
        "separation.  In twopi, specifies radial separation of concentric "
        "circles", label="Rank separation", graphviz=True)

    # Sets the aspect ratio (drawing height/drawing width) for the drawing.
    # Note that this is adjusted before the size attribute constraints are
    # enforced.
    #
    # If ratio is numeric, it is taken as the desired aspect ratio. Then, if
    # the actual aspect ratio is less than the desired ratio, the drawing
    # height is scaled up to achieve the desired ratio; if the actual ratio is
    # greater than that desired ratio, the drawing width is scaled up.
    #
    # If ratio = "fill" and the size attribute is set, node positions are
    # scaled, separately in both x and y, so that the final drawing exactly
    # fills the specified size.
    #
    # If ratio = "compress" and the size attribute is set, dot attempts to
    # compress the initial layout to fit in the given size. This achieves a
    # tighter packing of nodes but reduces the balance and symmetry. This
    # feature only works in dot.
    #
    # If ratio = "expand", the size attribute is set, and both the width and
    # the height of the graph are less than the value in size, node positions
    # are scaled uniformly until at least one dimension fits size exactly.
    # Note that this is distinct from using size as the desired size, as here
    # the drawing is expanded before edges are generated and all node and text
    # sizes remain unchanged.
    #
    # If ratio = "auto", the page attribute is set and the graph cannot be
    # drawn on a single page, then size is set to an ``ideal'' value. In
    # particular, the size in a given dimension will be the smallest integral
    # multiple of the page size in that dimension which is at least half the
    # current size. The two dimensions are then scaled independently to the new
    # size. This feature only works in dot.
#    ratio = Either(Float, Enum("fill", "compress", "expand", "auto"),
    ratio = Enum("fill", "compress", "expand", "auto",
        desc="aspect ratio (drawing height/drawing width) for the drawing",
        graphviz=True)

    # If true and there are multiple clusters, run cross minimization a second
    # time.
    remincross = Bool(False, desc="If true and there are multiple clusters, "
        "run cross minimization a second", label="Re-cross minimization",
        graphviz=True)

  # This is a synonym for the <html:a rel="attr">dpi</html:a> attribute.
    resolution = Alias("dpi", desc="a synonym for the dpi attribute",
        graphviz=True)

    # This specifies nodes to be used as the center of the
    # layout and the root of the generated spanning tree. As a graph attribute,
    # this gives the name of the node. As a node attribute (circo only), it
    # specifies that the node should be used as a central node. In twopi,
    # this will actually be the central node. In circo, the block containing
    # the node will be central in the drawing of its connected component.
    # If not defined,
    # twopi will pick a most central node, and circo will pick a random node.
    root = root_trait

  # If 90, set drawing orientation to landscape.
    rotate = Range(0, 360, desc="drawing orientation", graphviz=True)

    # During network simplex, maximum number of edges with negative cut values
    # to search when looking for one with minimum cut value.
    searchsize = Int(30, desc="maximum number of edges with negative cut "
        "values to search when looking for one with minimum cut value",
        label="Search size", graphviz=True)

    # Fraction to increase polygons (multiply
    # coordinates by 1 + sep) for purposes of determining overlap. Guarantees
    # a minimal non-zero distance between nodes.
    # If unset but <html:a rel="attr">esep</html:a> is defined, <html:a rel="attr">sep</html:a> will be
    # set to <html:code>esep/0.8</html:code>. If <html:a rel="attr">esep</html:a> is unset, the default value
    # is used.
    #
    # When <html:a rel="attr">overlap</html:a>="ipsep" or "vpsc",
    # <html:a rel="attr">sep</html:a> gives a minimum distance, in inches, to be left between nodes.
    # In this case, if <html:a rel="attr">sep</html:a> is a pointf, the x and y separations can be
    # specified separately.
    sep = Int(4, desc="Fraction to increase polygons (multiply coordinates by "
        "1 + sep) for purposes of determining overlap", label="Separation",
        graphviz=True)

  # Print guide boxes in PostScript at the beginning of
  # routesplines if 1, or at the end if 2. (Debugging)
    showboxes = showboxes_trait

    # Maximum width and height of drawing, in inches.
    # If defined and the drawing is too large, the drawing is uniformly
    # scaled down so that it fits within the given size.
    #
    # If <html:a rel="attr">size</html:a> ends in an exclamation point (<html:tt>!</html:tt>),
    # then it is taken to be
    # the desired size. In this case, if both dimensions of the drawing are
    # less than <html:a rel="attr">size</html:a>, the drawing is scaled up uniformly until at
    # least one dimension equals its dimension in <html:a rel="attr">size</html:a>.
    #
    # Note that there is some interaction between the <html:a rel="attr">size</html:a> and
    # <html:a rel="attr">ratio</html:a> attributes.
    size = pointf_trait

    # Controls how, and if, edges are represented. If true, edges are drawn as
    # splines routed around nodes; if false, edges are drawn as line segments.
    # If set to "", no edges are drawn at all.
    #
    # (1 March 2007) The values <html:span class="val">line</html:span> and <html:span class="val">spline</html:span> can be
    # used as synonyms for <html:span class="val">false</html:span> and <html:span class="val">true</html:span>, respectively.
    # In addition, the value <html:span class="val">polyline</html:span> specifies that edges should be
    # drawn as polylines.
    #
    # By default, the attribute is unset. How this is interpreted depends on
    # the layout. For dot, the default is to draw edges as splines. For all
    # other layouts, the default is to draw edges as line segments. Note that
    # for these latter layouts, if <html:code>splines="true"</html:code>, this
    # requires non-overlapping nodes (cf. <html:a rel="attr">overlap</html:a>).
    # If fdp is used for layout and <html:tt>splines="compound"</html:tt>, then the edges are
    # drawn to avoid clusters as well as nodes.
    splines = Enum("True", "False", "",
        desc="how, and if, edges are represented", graphviz=True)

    # Parameter used to determine the initial layout of nodes. If unset, the
    # nodes are randomly placed in a unit square with
    # the same seed is always used for the random number generator, so the
    # initial placement is repeatable.
    #
    #
    # has the syntax [style][seed].
    #
    # If style is present, it must be one of the strings "regular", "self", or
    # "random". In the first case, the nodes are placed regularly about a
    # circle. In the second case, an abbreviated version of neato is run to
    # obtain the initial layout. In the last case, the nodes are placed
    # randomly in a unit square.
    #
    # If seed is present, it specifies a seed for the random number generator.
    # If seed is a positive number, this is used as the seed. If it is anything
    # else, the current time, and possibly the process id, is used to pick a
    # seed, thereby making the choice more random. In this case, the seed value
    # is stored in the graph.
    #
    # If the value is just "random", a time-based seed is chosen.
    #
    # Note that input positions, specified by a node's pos attribute, are only
    # used when the style is "random".
    start = start_trait

  # A URL or pathname specifying an XML style sheet, used in SVG output.
    stylesheet = Str(desc="URL or pathname specifying an XML style sheet",
        label="Style sheet", graphviz=True)

    # If the object has a URL, this attribute determines which window
    # of the browser is used for the URL.
    # See <html:a href="http://www.w3.org/TR/html401/present/frames.html#adef-target">W3C documentation</html:a>.
    target = target_trait

    # If set explicitly to true or false, the value determines whether or not
    # internal bitmap rendering relies on a truecolor color model or uses
    # a color palette.
    # If the attribute is unset, truecolor is not used
    # unless there is a <html:a rel="attr">shapefile</html:a> property
    # for some node in the graph.
    # The output model will use the input model when possible.
    #
    # Use of color palettes results in less memory usage during creation of the
    # bitmaps and smaller output files.
    #
    # Usually, the only time it is necessary to specify the truetype model
    # is if the graph uses more than 256 colors.
    # However, if one uses <html:a rel="attr">bgcolor</html:a>=transparent with
    # a color palette, font
    # antialiasing can show up as a fuzzy white area around characters.
    # Using <html:a rel="attr">truecolor</html:a>=true avoids this problem.
    truecolor = Bool(True, desc="bitmap rendering relies on a truecolor color "
        "model or uses a color palette", graphviz=True)

    # Hyperlinks incorporated into device-dependent output.
    # At present, used in ps2, cmap, i*map and svg formats.
    # For all these formats, URLs can be attached to nodes, edges and
    # clusters. URL attributes can also be attached to the root graph in ps2,
    # cmap and i*map formats. This serves as the base URL for relative URLs in the
    # former, and as the default image map file in the latter.
    #
    # For svg, cmapx and imap output, the active area for a node is its
    # visible image.
    # For example, an unfilled node with no drawn boundary will only be active on its label.
    # For other output, the active area is its bounding box.
    # The active area for a cluster is its bounding box.
    # For edges, the active areas are small circles where the edge contacts its head
    # and tail nodes. In addition, for svg, cmapx and imap, the active area
    # includes a thin polygon approximating the edge. The circles may
    # overlap the related node, and the edge URL dominates.
    # If the edge has a label, this will also be active.
    # Finally, if the edge has a head or tail label, this will also be active.
    #
    # Note that, for edges, the attributes <html:a rel="attr">headURL</html:a>,
    # <html:a rel="attr">tailURL</html:a>, <html:a rel="attr">labelURL</html:a> and
    # <html:a rel="attr">edgeURL</html:a> allow control of various parts of an
    # edge. Also note that, if active areas of two edges overlap, it is unspecified
    # which area dominates.
    URL = Str(desc="hyperlinks incorporated into device-dependent output",
        label="URL", graphviz=True)

    # Clipping window on final drawing.
    #
    # "%lf,%lf,%lf,%lf,%lf" or "%lf,%lf,%lf,"%s""
    #
    # The viewPort W,H,Z,x,y or W,H,Z,N specifies a viewport for the final
    # image. The pair (W,H) gives the dimensions (width and height) of the
    # final image, in points. The optional Z is the zoom factor, i.e., the
    # image in the original layout will be W/Z by H/Z points in size. By
    # default, Z is 1. The optional last part is either a pair (x,y) giving a
    # position in the original layout of the graph, in points, of the center of
    # the viewport, or the name N of a node whose center should used as the
    # focus. By default, the focus is the center of the graph bounding box,
    # i.e., (bbx/2,bby/2), where "bbx,bby" is the value of the bounding box
    # attribute bb.
    #
    # Sample values: 50,50,.5,'2.8 BSD' or 100,100,2,450,300. The first will
    # take the 100x100 point square centered on the node 2.8 BSD and scale it
    # down by 0.5, yielding a 50x50 point final image.
    viewport = Tuple(Float, Float, Float, Float, Float, graphviz=True)
#    Either(
#        Tuple(Float, Float, Float, Float, Float),
#        Tuple(Float, Float, Float, Str),
#        desc="clipping window on final drawing"
#    )

    voro_margin = Float(0.05, desc="Factor to scale up drawing to allow "
        "margin for expansion in Voronoi technique. dim' = (1+2*margin)*dim.",
        label="Voronoi margin", graphviz=True)


#    def _defaultdist_default(self):
#        """ Trait initialiser """
#
#        return 1+(avg. len)*math.sqrt(|V|)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = tabbed_view
#    traits_view = graph_view

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, *args, **kw_args):
        """ Initialises the graph.
        """
        super(Graph, self).__init__(*args, **kw_args)

        # Listen for the addition or removal of nodes and update each branch's
        # list of available nodes so that they can move themselves.
        self.on_trait_change(self._on_nodes, "subgraphs*.nodes")
        self.on_trait_change(self._on_nodes, "subgraphs*.nodes_items")

        # Listen for the addition of edges and check that the heado_node and
        # tail_node instances exist in the graph or any subgraphs.
        self.on_trait_change(self._on_edges, "subgraphs*.edges")
        self.on_trait_change(self._on_edges, "subgraphs*.edges_items")


    def __str__(self):
        """ Returns a string representation of the graph in dot language. It
            will return the graph and all its subelements in string form.
        """
        s = ""
        if self.strict:
            s += "strict "

        if self.directed:
            s += "digraph"
        else:
            s += "graph"

        return "%s %s" % ( s, super(Graph, self).__str__() )

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    @on_trait_change("arrange")
    def arrange_all(self):
        """ Sets for the _draw_ and _ldraw_ attributes for each of the graph
            sub-elements by processing the xdot format of the graph.
        """
        import godot.dot_data_parser

        parser = godot.dot_data_parser.GodotDataParser()

        xdot_data = self.create( format = "xdot" )
#        print "GRAPH DOT:\n", str( self )
#        print "XDOT DATA:\n", xdot_data

        parser.dotparser.parseWithTabs()
        ndata = xdot_data.replace( "\\\n", "" )
        tokens = parser.dotparser.parseString( ndata )[0]
        parser.build_graph( graph=self, tokens=tokens[3] )

        self.redraw_canvas()


    @on_trait_change("redraw")
    def redraw_canvas(self):
        """ Parses the Xdot attributes of all graph components and adds
            the components to a new canvas.
        """
        from xdot_parser import XdotAttrParser

        xdot_parser = XdotAttrParser()
        canvas = self._component_default()

        for node in self.nodes:
            components = xdot_parser.parse_xdot_data( node._draw_ )
            canvas.add( *components )

            components = xdot_parser.parse_xdot_data( node._ldraw_ )
            canvas.add( *components )

        for edge in self.edges:
            components = xdot_parser.parse_xdot_data( edge._draw_ )
            canvas.add( *components )
            components = xdot_parser.parse_xdot_data( edge._ldraw_ )
            canvas.add( *components )
            components = xdot_parser.parse_xdot_data( edge._hdraw_ )
            canvas.add( *components )
            components = xdot_parser.parse_xdot_data( edge._tdraw_ )
            canvas.add( *components )
            components = xdot_parser.parse_xdot_data( edge._hldraw_ )
            canvas.add( *components )
            components = xdot_parser.parse_xdot_data( edge._tldraw_ )
            canvas.add( *components )

        self.component = canvas
        self.vp.request_redraw()


    def get_node(self, ID):
        """ Returns a node given an ID or None if no such node exists.
        """
        node = super(Graph, self).get_node(ID)
        if node is not None:
            return node

        for graph in self.all_graphs:
            for each_node in graph.nodes:
                if each_node.ID == ID:
                    return each_node
        else:
            return None


#    def write(self, path, prog=None, format=None):
#        """ Writes a graph to a file.
#
#            Given a filename 'path' it will open/create and truncate
#            such file and write on it a representation of the graph
#            defined by the dot object and in the format specified by
#            'format'.
#            The format 'raw' is used to dump the string representation
#            of the Dot object, without further processing.
#            The output can be processed by any of graphviz tools, defined
#            in 'prog', which defaults to 'dot'
#            Returns True or False according to the success of the write
#            operation.
#        """
#
#        if prog is None:
#            prog = self.program
#
#        if format is None:
#            format = self.format
#
#
#        dot_fd = None
#        try:
#            dot_fd = open( path, "wb" )
##            dot_fd = file( path, "w+b" )
#            if format == 'raw':
#                dot_fd.write( self.to_string() )
#            else:
#                dot_fd.write( self.create( prog, format ) )
#        finally:
#            if dot_fd is not None:
#                dot_fd.close()
#
#        return True

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _component_default(self):
        """ Trait initialiser.  Overrides the base class to use a Canvas
            for the root Graph.
        """
        return Canvas( draw_axes=True, bgcolor="lightsteelblue")


    def _epsilon_default(self):
        """ Trait initialiser.
        """
        if self.mode == "KK":
            return 0.0001 * len(self.nodes)
        else:
            return 0.0001


    def _maxiter_default(self):
        """ Trait initialiser.
        """
        mode = self.mode
        if mode == "KK":
            return 100 * len(self.nodes)
        elif mode == "major":
            return 200
        else:
            return 600

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get_all_graphs(self):
        """ Property getter.
        """
        top_graph = self

        def get_subgraphs(graph):
            assert isinstance(graph, BaseGraph)
            subgraphs = graph.subgraphs[:]
            for subgraph in graph.subgraphs:
                subsubgraphs = get_subgraphs(subgraph)
                subgraphs.extend(subsubgraphs)
            return subgraphs

        subgraphs = get_subgraphs(top_graph)
        return [top_graph] + subgraphs

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _directed_changed(self, new):
        """ Sets the connection string for all edges.
        """
        if new:
            conn = "->"
        else:
            conn = "--"

        for edge in [e for g in self.all_graphs for e in g.edges]:
            edge.conn = conn


    def _on_nodes(self):
        """ Maintains each branch's list of available nodes in order that they
            may move themselves (InstanceEditor values).
        """
        all_graphs = self.all_graphs
        all_nodes = [n for g in all_graphs for n in g.nodes]

        for graph in all_graphs:
            for edge in graph.edges:
                edge._nodes = all_nodes


    def _on_edges(self, object, name, old, new):
        """ Handles the list of edges for any graph changing.
        """
        if name == "edges_items":
            edges = new.added
        elif name == "edges":
            edges = new
        else:
            edges = []

        all_nodes = [n for g in self.all_graphs for n in g.nodes]

        for each_edge in edges:
            # Ensure the edge's nodes exist in the graph.
            if each_edge.tail_node not in all_nodes:
                object.nodes.append( each_edge.tail_node )

            if each_edge.head_node not in all_nodes:
                object.nodes.append( each_edge.head_node )

            # Initialise the edge's list of available nodes.
            each_edge._nodes = all_nodes


#    def _bgcolor_changed(self, new):
#        """ Handles the canvas background colour.
#        """
#        self.canvas.bgcolor = new

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

#    from godot.graph import Graph

    graph = Graph(ID="Foo", directed=True, label="Foo Graph")

    node1 = Node("node1", label="Node 1", shape="rectangle")
    graph.add_node( node1 )

    node2 = Node("node2", label="Node 2")
    graph.add_node( node2 )

    graph.add_edge(node1, node2)


#    subgraph1 = Subgraph(ID="subgraph1", rank="min")
#    subgraph1.nodes.append(Node("node3", label="Node 3"))
#    graph.subgraphs.append(subgraph1)
#
#    subgraph2 = Subgraph(ID="subgraph2", rank="max")
#    subgraph2.nodes.append(Node("node4", label="Node 4"))
#    subgraph1.subgraphs.append(subgraph2)

#    from godot.component.component_viewer import ComponentViewer
#    viewer = ComponentViewer(component=graph.component)
#    viewer.configure_traits()

#    graph.write("/tmp/graph.xdot", "dot", "xdot")

#    graph.arrange_all()

#    print write_dot_graph(graph)

    graph.configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
