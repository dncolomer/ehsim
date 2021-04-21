from itertools import combinations

import numpy as np
import sympy as sp
import sympy.physics.quantum as spq

# global variables
node_nb = 0

def getUID(prefix="id"):
    global node_nb

    node_nb = node_nb + 1
    return prefix + str(node_nb - 1)

class Node:
    def __init__(self, qubit, state=None, symbolic=True):
        self.uid = getUID("n")
        self.qubit = qubit

        self.state = state
        if (state is None):
            self.state = spq.Ket(0)
            if (symbolic):
                self.state = sp.symbols(self.uid+'_0')*spq.Ket(0) + sp.symbols(self.uid+'_1')*spq.Ket(1)

        self.measured = False
        self.edge_uid = None
        self.replaced = False

class Hyperedge:
    def __init__(self, weight, uid=None):
        self.node_uids = []
        if uid is None:
            self.uid = getUID("edge")
        else:
            self.uid = uid
        self.weight = weight

class Hypergraph:
    # TODO add support for register level operation in a later version
    def __init__(self, nb_qubits: int, sv: list = None, record_gates: bool = True, symbolic: bool = True):
        """
        Create a new Hypergraph simulator.

        Arguments:
            nb_qubits (int): The number of qubits to simulate
            sv (list): A list of state vectors to initialize with
            record_gates (bool: True): Whether to keep a log of gates as they
                are applied. This incurs a slight performance penalty but
                enables some useful tools like visualization.

        """
        global node_nb

        self.nodes = {}
        self.edges = {}
        self.qubitLabels = []

        sv = sv or []

        self._record_gates = record_gates
        self._gate_log = []
        self._num_qubits = nb_qubits

        node_nb = 0

        if len(sv) > 0:
            #TODO
            pass
        else:
            for i in range(0, nb_qubits):
                self.qubitLabels.append("q" + str(i))

                node = Node("q" + str(i), symbolic=symbolic)
                self.nodes[node.uid] = node

###############################################################
# UTILS
###############################################################

    def stateEq(self, s1, s2):
        s10_abs = sp.Abs(s1.coeff(spq.Ket(0)))
        s10_arg = sp.arg(s1.coeff(spq.Ket(0)))

        s20_abs = sp.Abs(s2.coeff(spq.Ket(0)))
        s20_arg = sp.arg(s2.coeff(spq.Ket(0)))

        s11_abs = sp.Abs(s1.coeff(spq.Ket(1)))
        s11_arg = sp.arg(s1.coeff(spq.Ket(1)))

        s21_abs = sp.Abs(s2.coeff(spq.Ket(1)))
        s21_arg = sp.arg(s2.coeff(spq.Ket(1)))

        s1_relphase =  sp.Abs(s11_arg - s10_arg)
        s2_relphase =  sp.Abs(s21_arg - s20_arg)

        return s1_relphase == s2_relphase and s10_abs == s20_abs and s11_abs == s21_abs

    def _record(self, qubits, gate: np.ndarray, controls: list = None):
        """
        Make a note of which gates have been applied to which qubits.

        Arguments:
            qubits (str | list[str]): A list of qubits or a single qubit name
            gate: The gate that was applied
            controls (optional): A list of control qubits

        Returns:
            None

        """
        if not self._record_gates:
            return
        # If this gate acts on a single qubit, save it as an array of length=1.
        # This will make the gate log types consistent.
        if isinstance(qubits, str):
            qubits = [qubits]
        self._gate_log.append(
            {"gate": gate, "qubits": qubits, "controls": controls or []}
        )

    def __len__(self):
        return self._num_qubits

    def getQubitNodeIds(self, qubit):
        uids = []
        for n in self.nodes:
            if self.nodes[n].qubit == qubit:
                uids.append(self.nodes[n].uid)

        return uids

    def getQubitNodeIdInEdge(self, qubit, edge_uid):
        for n in self.nodes:
            if self.nodes[n].qubit == qubit:
                if (self.nodes[n].edge_uid is None and edge_uid is None) or (
                    self.nodes[n].edge_uid == edge_uid
                ):
                    return self.nodes[n].uid

        return None

    def getQubitNodeId(self, qubit, edge):
        uids = []
        for n in self.edges[edge].node_uids:
            if self.nodes[n].qubit == qubit:
                return self.nodes[n].uid

        return None

    def getQubitEdgeIds(self, qubit):
        uids = []
        for e in self.edges:
            node_uids = self.edges[e].node_uids
            for node_uid in node_uids:
                if self.nodes[node_uid].qubit == qubit:
                    uids.append(e)

        return uids

    def addNodeToEdge(self, node_uid, edge_uid):
        # assume edge and node exist
        if self.nodes[node_uid].edge_uid == None:
            self.nodes[node_uid].edge_uid = edge_uid
            self.edges[edge_uid].node_uids.append(node_uid)

    def moveNodeToEdge(self, node_uid, src_edge_uid, target_edge_uid):
        # assign to target
        self.nodes[node_uid].edge_uid = target_edge_uid
        #pop from src
        self.edges[src_edge_uid].node_uids.pop(self.edges[src_edge_uid].node_uids.index(node_uid))
        #append to target
        self.edges[target_edge_uid].node_uids.append(node_uid)

    def deleteNode(self, node_uid):
        # assuming nodes only belong to one element
        if node_uid in self.nodes.keys():
            e_uid = self.nodes[node_uid].edge_uid

            self.nodes.pop(node_uid)

            if e_uid in self.edges.keys():
                i = self.edges[e_uid].node_uids.index(node_uid)
                self.edges[e_uid].node_uids.pop(i)

    def deleteEdge(self, edge_uid):
        for nid in self.edges[edge_uid].node_uids:
            self.nodes.pop(nid)

        self.edges.pop(edge_uid)

###############################################################
# MERGE STATES
###############################################################

    #This is where we merge single system states into one edge superposing the comp. basis 
    def mergeStates(self, qubits):
        pass

###############################################################
# SPLIT STATES
###############################################################

    #This is where we split single system states into one edge per computational base 
    def splitStates(self, qubits):
        pass

###############################################################
# SIMPLIFY
###############################################################

    #This is to apply interference effects
    #Can only be done if all qubits can be composed
    def simplifyQubits(self, qubits):
        pass

###############################################################
# COMPOSE
###############################################################
    
    def composeEdges(base_e, cand_e, qubits):
        pass

    def canComposeEdges(base_e, cand_e, qubits):
        pass
    
    def composeRec(eids, qubits):
        pass

    def composeQubits(self, qubits):
        pass

###############################################################
# DECOMPOSE
###############################################################

    def decomposeEdges(base_e, cand_e, qubits):
        new_e = Hyperedge(1)
        for q in qubits:
            base_n = self.getQubitNodeIdInEdge(q,base_e)
            cand_n = self.getQubitNodeIdInEdge(q,cand_e)

            self.moveNodeToEdge(base_n,base_e,new_e)
            self.deleteNode(cand_n)
            

    def canDecomposeEdges(base_e, cand_e, qubits):
        for q in qubits:
            base_n = self.getQubitNodeIdInEdge(q,base_e)
            cand_n = self.getQubitNodeIdInEdge(q,cand_e)

            if (not self.stateEq(self.nodes[base_n].state, self.nodes[cand_e].state)):
                return False

        return True

    def decomposeRec(eids, qubits):
        if (len(eids)) <= 1:
            return eids

        for i, base_e in enumerate(eids):
            for j, cand_e in enumerate(eids):
                if (i != j and self.canDecomposeEdges(base_e, cand_e, qubits)):
                    self.decomposeEdges(base_e, cand_e, qubits)
                    
                    #Update the list of edge ids
                    eids.remove(base_e)
                    eids.remove(cand_e)

                    return self.decomposeRec(eids, qubits)
        
        return eids

    def decomposeQubits(self, qubits):
        eids_base = []

        # Check if we can decompose
        for i,q in enumerate(qubits):
            if (i == 0):
                eids_base = self.getQubitEdgeIds(q)
            else:
                if (set(eids_base) != self.getQubitEdgeIds(q)):
                    print("The given qubits can't be factored")
                    return None
        
        return decomposeRec(eids_base, qubits)

###############################################################
# REWRITE
###############################################################

    # match [1,1,0]
    # edge {uid = ...}
    # map ["q0","q1","q2"]
    def isMatch(self,match,edge,qubit_map):
        euid = None
        if (edge is not None):
            euid = self.edges[edge].uid

        for i,m in enumerate(match):
            q = qubit_map[i] #TODO check for error

            if (self.getQubitNodeIdInEdge(q,euid) is None):
                return False
            else:
                node = self.nodes[self.getQubitNodeIdInEdge(q,euid)]
                if (not self.stateEq(node.state,m)):
                    return False

        return True
    
    def replaceMatch(self,edge,replace,qubit_map):
        euid = None
        if (edge is not None):
            euid = self.edges[edge].uid

        for i,m in enumerate(replace):
            q = qubit_map[i] #TODO check for error

            if (not self.nodes[self.getQubitNodeIdInEdge(q,euid)].replaced):
                self.nodes[self.getQubitNodeIdInEdge(q,euid)].state = m

                m = sp.simplify(m)
                m = sp.expand(m)

                self.nodes[self.getQubitNodeIdInEdge(q,euid)].replaced = True

    #qubit_map=["q0","q1","q2"]
    def rewrite(self,rules,qubit_map,params_map=[]):
        #TODO need to refactor this too account for rules and qubit mappings
        #self._record(qubit, rules['name'])

        #set all replacement tracking t False
        for n in self.nodes:
            self.nodes[n].replaced = False

        for rule in rules['rules']:
            #find matches in edges
            # TODO if th edge has been touched previously shouldnt match anymore
            for e in self.edges:
                if (self.isMatch(rule['match'],e,qubit_map)):
                    self.replaceMatch(e,rule['replace'],qubit_map)
            
            #find matches in system
            if (self.isMatch(rule['match'],None,qubit_map)):
                    self.replaceMatch(None,rule['replace'],qubit_map)

###############################################################
# MEASURE
###############################################################

    def measure(self, qubits):
        # iterate over each hyper edge the qubit is in
        for q in qubits:
            edge_ids = self.getQubitEdgeIds(q)
            if len(edge_ids) == 0:
                # if the qubit is in the comp. basis then we just flag it as measured = True
                # remve any global phase
                # Note: Quirk keeps track of the phase so that a statevector (assuming measurement deferred can still be shown)
                # self.nodes[node.uid].state = self.correctPhase(node.state)
                node = self.nodes[self.getQubitNodeIdInEdge(q, None)]
                self.nodes[node.uid].measured = True
                if not self.stateEq(node.state, spq.Ket(1)) and not self.stateEq(
                    node.state, spq.Ket(0)
                ):
                    # if the qubit is not then we need to split the edge into 2.
                    # One where the node will be in the 0 state + measured = True
                    # One where the node will be in the 1 state + measured = True
                    self.splitEdgeZ(None, node.qubit)
            else:
                for e_id in edge_ids:
                    # if the qubit is in the comp. basis then we just flag it as measured = False
                    # remve any global phase
                    # Note: Quirk keeps track of the phase so that a statevector (assuming measurement deferred can still be shown)
                    # self.nodes[node.uid].state = self.correctPhase(node.state)
                    node = self.nodes[self.getQubitNodeIdInEdge(q, e_id)]
                    self.nodes[node.uid].measured = True
                    if not self.stateEq(node.state, spq.Ket(1)) and not self.stateEq(
                        node.state, spq.Ket(0)
                    ):
                        # if the qubit is not then we need to split the edge into 2.
                        # One where the node will be in the 0 state + measured = True
                        # One where the node will be in the 1 state + measured = True
                        self.splitEdgeZ(e_id, node.qubit)

        return

    # TODO calculate how much we are omitting (like Quirk does)
    def postSelectZ(self, qubits, state):
        self.measure(qubits)
        loss = 0
        for qubit in qubits:
            nodeIds = self.getQubitNodeIds(qubit)
            for nodeId in nodeIds:
                node = self.nodes[nodeId]
                if (not self.stateEq(node.state, state)):
                    if (node.edge_uid is not None):
                        edge = self.edges[node.edge_uid]
                        '''loss = loss + (
                            edge.weight.real ** 2 + edge.weight.imag ** 2
                        )'''

                    self.deleteEdge(node.edge_uid)

        return loss