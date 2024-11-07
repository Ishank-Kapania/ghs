import sys
from collections import deque
from mpi4py import MPI
from mpi4py.MPI import Request

# Constants
INF = 100000

class ConstantNamespace:
    def __init__(self):
        self._constants = {}
        self._counter = 0
    def __getattr__(self, key):
        if key.isupper():
            if key not in self._constants:
                self._counter += 1
                self._constants[key] = self._counter
            return self._constants[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
MESSAGE_TYPES = ConstantNamespace()
class MessageType:
    CONNECT = MESSAGE_TYPES.CONNECT
    INITIATE = MESSAGE_TYPES.INITIATE
    TEST = MESSAGE_TYPES.TEST
    ACCEPT = MESSAGE_TYPES.ACCEPT
    REJECT = MESSAGE_TYPES.REJECT
    REPORT = MESSAGE_TYPES.REPORT
    CHANGEROOT = MESSAGE_TYPES.CHANGEROOT
    TERMINATE = MESSAGE_TYPES.TERMINATE

class Node:
    def __init__(self):
        self.start_time = None
        self.testwait = 0
        self.connectwait = 0
        self.reportwait = 0
        self.waiting = deque()
        self.edges = []
        self.level = 0
        self.name = 0
        self.parent = 0
        self.state = 0
        self.node_id = None
        self.n = 0
        self.best_weight = INF
        self.best_node_id = None
        self.rec = 0
        self.test_node_id = None
        self.halt = False

    def get_weight(self, index):
        return self.edges[index][0]

    def get_flag(self, index):
        return self.edges[index][1]

    def get_node_id(self, index):
        return self.edges[index][2]

    def input_file(self, file):
        with open(file, 'r') as f:
            N = int(f.readline().strip())
            for i in range(self.node_id):
                line = f.readline().strip().split()
                for j in range(N):
                    temp = int(line[j])
            line = f.readline().strip().split()
            for i in range(N):
                temp = int(line[i])
                if temp != INF:
                    self.edges.append((temp, 0, i))
            for i in range(self.node_id + 1, N):
                line = f.readline().strip().split()
                for j in range(N):
                    temp = int(line[j])
        self.n = len(self.edges)
        self.edges.sort()
(weight,flag ,node id)
    def initialize(self, comm, verbose):
        if verbose:
            self.log_message(f"initialization")
        self.edges[0] = (self.edges[0][0], 1, self.edges[0][2])
        self.level = 0
        self.state = 2
        self.rec = 0
        self.connectwait = 0
        self.reportwait = 0
        if not self.connectwait:
            self.connectwait = 1
            self.send_message(comm, self.get_node_id(0), MessageType.CONNECT, 0, verbose)

    def connect(self, source_node_id, level, comm, verbose):
        index = self.find_edge_index(source_node_id)
        if level < self.level:
            self.edges[index] = (self.edges[index][0], 1, self.edges[index][2])
            if verbose:
                self.log_branch_edge(source_node_id)
            self.send_message(comm, source_node_id, MessageType.INITIATE, [self.level, self.name, self.state], verbose)
        elif self.get_flag(index) == 0:
            self.waiting.append((MessageType.CONNECT, [source_node_id, level]))
            if verbose:
                self.log_waiting_message("connect", [source_node_id, level])
        else:
            self.send_message(comm, source_node_id, MessageType.INITIATE, [self.level + 1, self.get_weight(index), 1], verbose)

    def report(self, comm, verbose):
        count = sum(1 for i in range(self.n) if self.get_flag(i) == 1 and self.get_node_id(i) != self.parent)
        if self.rec == count and self.test_node_id == -1 and not self.reportwait:
            self.reportwait = 1
            self.state = 2
            self.send_message(comm, self.parent, MessageType.REPORT, self.best_weight, verbose)

    def find_min(self, comm, verbose):
        found = 0
        for i in range(self.n):
            if self.get_flag(i) == 0 and not self.testwait:
                self.testwait = 1
                found = 1
                self.test_node_id = self.get_node_id(i)
                self.send_message(comm, self.test_node_id, MessageType.TEST, [self.level, self.name], verbose)
                break
        if not found:
            self.test_node_id = -1
            self.report(comm, verbose)

    def initiate(self, source_node_id, level, name, state, comm, verbose):
        self.level = level
        self.name = name
        self.state = state
        self.parent = source_node_id
        self.best_node_id = -1
        self.best_weight = INF
        self.test_node_id = -1
        self.connectwait = 0
        self.reportwait = 0
        self.send_initiate_to_neighbors(comm, verbose)
        if self.state == 1:
            self.rec = 0
            self.find_min(comm, verbose)

    def send_initiate_to_neighbors(self, comm, verbose):
        for i in range(self.n):
            if self.get_flag(i) == 1 and self.get_node_id(i) != self.parent:
                self.send_message(comm, self.get_node_id(i), MessageType.INITIATE, [self.level, self.name, self.state], verbose)

    def change_root(self, comm, verbose):
        index = self.find_edge_index(self.best_node_id)
        if self.get_flag(index) == 1:
            self.send_message(comm, self.best_node_id, MessageType.CHANGEROOT, 0, verbose)
        else:
            self.edges[index] = (self.edges[index][0], 1, self.edges[index][2])
            if verbose:
                self.log_branch_edge(self.best_node_id)
            if not self.connectwait:
                self.connectwait = 1
                self.send_message(comm, self.best_node_id, MessageType.CONNECT, self.level, verbose)

    def report_recv(self, source_node_id, weight, comm, verbose):
        if source_node_id != self.parent:
            if weight < self.best_weight:
                self.best_weight = weight
                self.best_node_id = source_node_id
            self.rec += 1
            self.report(comm, verbose)
        else:
            if self.state == 1:
                self.waiting.append((MessageType.REPORT, [source_node_id, weight]))
                if verbose:
                    self.log_waiting_message("report", [source_node_id, weight])
            elif weight > self.best_weight:
                self.change_root(comm, verbose)
            elif weight == self.best_weight and self.best_weight == INF:
                self.halt = True
                self.send_terminate_to_neighbors(comm, verbose)

    def send_terminate_to_neighbors(self, comm, verbose):
        for i in range(self.n):
            if self.get_flag(i) == 1:
                self.send_message(comm, self.get_node_id(i), MessageType.TERMINATE, 1, verbose)

    def test(self, source_node_id, level, name, comm, verbose):
        index = self.find_edge_index(source_node_id)
        if level > self.level:
            self.waiting.append((MessageType.TEST, [source_node_id, level, name]))
            if verbose:
                self.log_waiting_message("test", [source_node_id, level, name])
        elif name == self.name:
            if self.get_flag(index) == 0:
                self.edges[index] = (self.edges[index][0], -1, self.edges[index][2])
            if self.get_node_id(index) != self.test_node_id:
                self.send_message(comm, source_node_id, MessageType.REJECT, 0, verbose)
            else:
                self.find_min(comm, verbose)
        else:
            self.send_message(comm, source_node_id, MessageType.ACCEPT, 0, verbose)

    def accept(self, source_node_id, comm, verbose):
        index = self.find_edge_index(source_node_id)
        self.test_node_id = -1
        if self.get_weight(index) < self.best_weight:
            self.best_weight = self.get_weight(index)
            self.best_node_id = source_node_id
        self.report(comm, verbose)

    def reject(self, source_node_id, comm, verbose):
        index = self.find_edge_index(source_node_id)
        if self.get_flag(index) == 0:
            self.edges[index] = (self.edges[index][0], -1, self.edges[index][2])
        self.find_min(comm, verbose)

    def send_message(self, comm, dest, tag, message, verbose):
        if verbose:
            self.log_send_message(dest, tag, message)
        request = comm.isend(message, dest=dest, tag=tag)
        request.wait()

    def find_edge_index(self, node_id):
        for i in range(self.n):
            if self.get_node_id(i) == node_id:
                return i
        return None

    def log_message(self, message):
        print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} {message}")

    def log_branch_edge(self, node_id):
        print(f"Branch Edge - {min(self.node_id, node_id)} {max(self.node_id, node_id)}")

    def log_waiting_message(self, message_type, args):
        if message_type == "connect":
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is waiting for a connect message from node {args[0]} at level {args[1]}")
        elif message_type == "report":
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is waiting with node {args[0]} and weight {args[1]}")
        elif message_type == "test":
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is waiting for a test message from node {args[0]} at level {args[1]} with name {args[2]}")

    def log_send_message(self, dest, tag, message):
        if tag == MessageType.CONNECT:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a connect message to node {dest} with level {message}")
        elif tag == MessageType.INITIATE:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending an initiate message to node {dest} with level {message[0]}, name {message[1]}, and state {message[2]}")
        elif tag == MessageType.TEST:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a test message to node {dest} with level {message[0]} and name {message[1]}")
        elif tag == MessageType.ACCEPT:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending an accept message to node {dest}")
        elif tag == MessageType.REJECT:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a reject message to node {dest}")
        elif tag == MessageType.REPORT:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a report message to node {dest} with best weight {message}")
        elif tag == MessageType.CHANGEROOT:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a changeroot message to node {dest}")
        elif tag == MessageType.TERMINATE:
            print(f"Node {self.node_id} at Name: {self.name} and Level: {self.level} is sending a terminate message to node {dest}")

def main():
    comm = MPI.COMM_WORLD
    node = Node()
    node.node_id = comm.Get_rank()
    verbose = "-v" in sys.argv
    if verbose:
        print(f"Node {node.node_id} has entered the main function")
    node.input_file(sys.argv[1])
    comm.Barrier()
    node.start_time = MPI.Wtime()
    node.initialize(comm, verbose)
    while True:
        if comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
            msg_info = MPI.Status()
            msg = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=msg_info)
            if msg_info.Get_tag() == MessageType.CONNECT:
                level = msg
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a connect message from node {source_node_id} with level {level}")
                node.connect(source_node_id, level, comm, verbose)
            elif msg_info.Get_tag() == MessageType.INITIATE:
                level = msg[0]
                name = msg[1]
                state = msg[2]
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received an initiate message from node {source_node_id} with level {level}, name {name}, and state {state}")
                node.initiate(source_node_id, level, name, state, comm, verbose)
            elif msg_info.Get_tag() == MessageType.TEST:
                level = msg[0]
                name = msg[1]
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a test message from node {source_node_id} with level {level} and name {name}")
                node.test(source_node_id, level, name, comm, verbose)
            elif msg_info.Get_tag() == MessageType.ACCEPT:
                node.testwait = 0
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received an accept message from node {source_node_id}")
                node.accept(source_node_id, comm, verbose)
            elif msg_info.Get_tag() == MessageType.REJECT:
                node.testwait = 0
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a reject message from node {source_node_id}")
                node.reject(source_node_id, comm, verbose)
            elif msg_info.Get_tag() == MessageType.REPORT:
                weight = msg
                source_node_id = msg_info.Get_source()
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a report message from node {source_node_id} with weight {weight}")
                node.report_recv(source_node_id, weight, comm, verbose)
            elif msg_info.Get_tag() == MessageType.CHANGEROOT:
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a changeroot message from node {msg_info.Get_source()}")
                node.change_root(comm, verbose)
            elif msg_info.Get_tag() == MessageType.TERMINATE:
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} has received a terminate message from node {msg_info.Get_source()}")
                for i in range(node.n):
                    if node.get_flag(i) == 1 and node.get_node_id(i) != msg_info.Get_source():
                        node.send_message(comm, node.get_node_id(i), MessageType.TERMINATE, 0, verbose)
                break
        if node.waiting:
            element = node.waiting.popleft()
            if element[0] == MessageType.CONNECT:
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} is resolving a waiting connect message with node {element[1][0]} at level {element[1][1]}")
                node.connect(element[1][0], element[1][1], comm, verbose)
            elif element[0] == MessageType.REPORT:
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} is resolving a waiting report message with node {element[1][0]} and best weight {element[1][1]}")
                node.report_recv(element[1][0], element[1][1], comm, verbose)
            elif element[0] == MessageType.TEST:
                if verbose:
                    print(f"Node {node.node_id} at Name: {node.name} and Level: {node.level} is resolving a waiting test message with node {element[1][0]} at level {element[1][1]} and name {element[1][2]}")
                node.test(element[1][0], element[1][1], element[1][2], comm, verbose)
        if node.halt:
            break
    if not verbose:
        for i in range(node.n):
            if node.get_flag(i) == 1 and node.get_node_id(i) > node.node_id:
                print(f"{node.node_id} {node.get_node_id(i)} {node.get_weight(i)}")
    comm.Barrier()
    MPI.Finalize()

if __name__ == '__main__':
    main()