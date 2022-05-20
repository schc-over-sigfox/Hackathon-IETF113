from Messages.Header import Header

def zfill(string, width):
    if len(string) < width:
        return ("0" * (width - len(string))) + string
    else:
        return string

class Fragment:

    profile = None
    header_length = 0
    rule_id_size = 0
    t = 0
    n = 0
    window_size = 0

    header = None
    payload = None

    def __init__(self, profile, fragment):
        self.profile = profile

        self.header_length = profile.HEADER_LENGTH
        self.rule_id_size = profile.RULE_ID_SIZE
        self.t = profile.T
        self.n = profile.N
        self.m = profile.M

        header = zfill(str(bin(int.from_bytes(fragment[0], 'big')))[2:], self.header_length)
        payload = fragment[1]

        rule_id = str(header[:self.rule_id_size])
        dtag = str(header[self.rule_id_size:self.rule_id_size + self.t])
        window = str(header[self.rule_id_size + self.t:self.rule_id_size + self.t + self.m])
        fcn = str(header[self.rule_id_size + self.t + self.m:self.rule_id_size + self.t + self.m + self.n])
        c = ""


        self.header = Header(self.profile, rule_id, dtag, window, fcn, c)

        self.payload = payload

    def test(self):
        print("Header: " + self.header.string)
        print("Payload: " + str(self.payload))

    def is_all_1(self):
        for N in self.header.FCN:
            # print("All 1 -> N: {}".format(N))
            if N == "0":
                # print("FALSE not all-1")
                return 
        return True
        # fcn = self.header.FCN
        # fcn_set = set()
        # for x in fcn:
        #     fcn_set.add(x)
        # return len(fcn_set) == 1 and "1" in fcn_set

    def is_all_0(self):
        for N in self.header.FCN:
            # print("All 0 -> N: {}".format(N))
            if N == "1":
                # print("FALSE not all-0")
                return False
        return True
        # fcn = self.header.FCN
        # fcn_set = set()
        # for x in fcn:
        #     fcn_set.add(x)
        # return len(fcn_set) == 1 and "0" in fcn_set

    def is_sender_abort(self):
        fcn = self.header.FCN
        padding = self.payload.decode()
        for N in fcn:
            print("N: {}".format(N))
            if N == 0:
                return False
        # All the fcn values are 1
        for bit in padding:
            print('bit: {}'.format(bit))
            if bit == 1:
                return False
        # All padding is 0
        return True

