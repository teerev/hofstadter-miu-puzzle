from numpy import random
import pandas as pd
import pygraphviz as pgv
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


class muPuzzle:
    
    """
    A class to represent Douglas Hofstadter's impossible MU-puzzle and its variants
    based on a starting string (The axiom.).
    """
    
    def __init__(self, axiom):
        self.axiom = axiom


    @staticmethod
    def rule_one_possible(string):
        
        """
        Returns True or False depending on whether the last letter of the current
        string is 'I'.
        """
        
        if string[-1:] == 'I':
            return True  
        else:
            return False


    @staticmethod
    def rule_two_possible(string):
        
        """
        Returns True or False depending on whether the first letter of the current
        string is 'M'.
        """
        
        if string[:1] == 'M':
            return True
        else:
            return False
    
    
    @staticmethod
    def rule_three_possible(string):
        
        """
        Returns True or False depending on whether the current string contains 'III'.
        """
         
        if string.find('III') != -1:
            return True
        else:
            return False
        
        
    @staticmethod
    def rule_four_possible(string):
        
        """
        Returns True or False depending on whether the current string contains 'UU'.
        """
        
        if string.find('UU') != -1:
            return True
        else:
            return False    

        
    @staticmethod
    def rule_three_indices(string):
        
        """
        Returns list of indices, if any, at which rule three can be applied to a string,
        """
        
        return [index for index, char in enumerate(string) if string.startswith('III', index)]
     
    
    def get_options(self, string):
    
        """
        Returns dictionary of rules (values) that can be applied to the current string
        and the corresponding resultant strings (keys).
        """
        
        options = dict()
    
        if self.rule_one_possible(string):
            options[self.apply_rule_one(string)] = '1'
    
        if self.rule_two_possible(string):
            options[self.apply_rule_two(string)] = '2'
    
        # Applying rule three generally involves a for loop because it can be applied at different 
        # indices in the string. For example 'MIIIIU' can be mapped to either 'MUIU' or 'MIUU'.
        if self.rule_three_possible(string):
            for index in self.rule_three_indices(string):
                options[self.apply_rule_three(string, index)] = f'3i{index}'
            
        if self.rule_four_possible(string):
            options[self.apply_rule_four(string)] = '4'
    
        return options
    
    
    def apply_rule_one(self, string):
        
        """
        For input string of format 'xI', returns 'xIU'.
        """
        
        if self.rule_one_possible(string):
            return f'{string}U'
        else:
            return None
    

    def apply_rule_two(self, string):
        
        """
        For input string of format 'Mx', returns 'Mxx'.
        """
        
        if self.rule_two_possible(string):
            return f'{string}{string[1:]}'    
        else:
            return None
    
    
    def apply_rule_three(self, string, index):
        
        """
        For input string (and index) of format 'xIIIy', returns 'xUy'. 
        """
        
        if self.rule_three_possible(string):
            return f'{string[:index]}U{string[index+3:]}'
        else:
            return None
    
    
    def apply_rule_four(self, string):
        
        """
        For input string of format 'xUUy', returns 'xy'.
        """

        if self.rule_four_possible(string):
            index = string.find('UU')
            return f'{string[:index]}{string[index+2:]}'
        else:
            return None
    

    def random_walk(self, num_steps):
    
        """
        Given a starting string (axiom) and a number of steps, returns a dictionary of resultant strings
        and the rules used to get those strings. Can be thought of as a random walk through the 
        directed graph of available strings (nodes) accessible by the available rules (edges).
        """
        # dictionary to collect nodes encountered in random path
        path = dict()
        
        # variable to store current string, starting with the axiom
        string = self.axiom
        
        # storage list for nodes randomly encountered at each step, starting with the axiom
        strings = [string,]
        
        # storage list for rules corresponding to randomly chosen nodes
        rules = [None,]
        
        i=0    
        # for each step, assess which rules can be applied at the current node and apply one randomly
        while i < num_steps:
            
            # see which rules can be applied to the current node, and the new nodes these result in
            options = self.get_options(string)
            
            # choose a one of the newly discovered nodes at random
            string = random.choice(list(options.keys()))
            
            # take note of the rule required to move to the randomly chosen node
            rule = options[string]

            # store the randomly chosen node and the rule required to each it in the storage lists
            strings.append(string)
            rules.append(rule)

            i+=1

        path['rules'] = rules
        path['strings'] = strings

        return path


    def discover_local_network(self, num_steps):
        
        """
        Returns a nested dictionary of all possible resultant strings (nodes) accessible by the available
        rules (edges) from a starting string (axiom; also a node) within a maximum number of applications
        of the rules (num_steps). i.e. finds all possible strings accessible by all possible combinations
        of rules 1-4 applied up a maximum of num_steps times. Works by propagating outwards from the
        axiom node and adding all neighbouring nodes to the network at each step. 
        
        WARNING: Total number of nodes in network increases multiplicatively with num_steps, so scales 
        poorly for num_steps > 6.
        """
        
        # create a set into which discovered nodes will be added, starting with the axiom node 
        nodes = {self.axiom,}
        
        # create a dictionary into which discovered edges will be added with (node, neighbouring 
        # node) tuple as dict key, and rule that gives node ---> neighbour as dict value
        edges = dict()

        i=0
        
        # find all nodes resulting from all possible combinations of rules 1-4 up to num_steps times
        while i<num_steps:
            
            # list to collect all new nodes found in each step
            new_neighbours = []
            
            # iterate over all nodes in the current network as of num_steps
            for node in nodes:
                
                # get all nodes accessible from the current node and the corresponding rules
                neighbour_rule_pairs = self.get_options(node)
            
                # iterate over the newly discovered neighbouring nodes adjacent to the current node
                for neighbour, rule in neighbour_rule_pairs.items():
                    
                    # for each neighbouring node, store the node--> neighbour edge and corresponding rule
                    edges[tuple([node, neighbour])] = rule

                    # store these neighbouring nodes 
                    new_neighbours.append(neighbour)

            # store all nodes discovered in this step into the nodes list comprising the entire network
            for new_neighbour in new_neighbours:
                nodes.add(new_neighbour)
            
            i+=1

        network = dict()
        network['nodes'] = nodes
        network['edges'] = edges

        return network
    
    
    @staticmethod
    def get_adjacency_matrix(network):
        
        """
        Returns pandas dataframe representing the adjacency matrix for the network structure found by
        discover_local_network(), whose index and columns attributes are set to the node names (strings).
        """
    
        adjacency = pd.DataFrame(0, index=network['nodes'], columns=network['nodes'])
    
        for nodepair, rule in network['edges'].items():
            adjacency.loc[nodepair[1], nodepair[0]] = rule
        
        return adjacency


    @staticmethod
    def plot_network(network):
        
        """
        Returns an image showing the graph of the network found by discover_local_network().
        """
    
        plt.rcParams['figure.dpi'] = 400
        
        graph = pgv.AGraph(directed=True, overlap='false', splines='true')
        
        for node in network['nodes']:
            graph.add_node(node)
        
        for edge in network['edges'].items():
            graph.add_edge(edge[0], label=edge[1], color='red')
        
        graph.layout(prog='neato')  #neato, dot, twopi, circo, fdp, nop, wc, acyclic, gvpr, gvcolor, ccomps, sccmap, sfdp
        graph.draw('graph.png')
        
        img = mpimg.imread('graph.png')
        plt.imshow(img)
        plt.axis('off')
        plt.show()
