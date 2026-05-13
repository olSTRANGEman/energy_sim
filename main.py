import argparse
import csv

class Generator:

    def __init__(self, id: str, type: str, consume: float, output_per_hour: list):
        self.id = id
        self.type = type 
        self.consume = consume 
        self.output_per_hour = output_per_hour 

    def get_consume(self):
        return self.consume

    def get_output(self):
        return self.output_per_hour
    
    def get_id(self):
        return self.id



def gens_and_cons(generators: list, consumers: list) -> list:
    #Greedy using energy
    generators= sorted(generators, key = lambda x: x.get_consume())    
    gen_shedule = {}
    con_scedule = {}

    for h in range(24):
        #Greedy giving energy
        consumers = sorted(consumers, key = lambda x: x[1][h])     
        work_gens = [x for x in generators if x.get_output()[h] != 0]
        gen_out, consump_in = 0, 0  
        people_id, gen_id = set(), set()
        id_to_activate = 0

        for i in range(len(consumers)):


            while gen_out < (consump_in + consumers[i][1][h]):
                if len(gen_id)+1 > len(work_gens):
                    break
                gen_out += work_gens[id_to_activate].get_output()[h]
                gen_id.add(work_gens[id_to_activate].get_id())
                id_to_activate += 1
            else:
                consump_in += consumers[i][1][h]
                people_id.add(consumers[i][0])
        gen_shedule[h] = gen_id
        con_scedule[h] = people_id
        online = sorted([x for x in generators if x.get_id() in gen_id], key = lambda x: x.get_output()[h], reverse=True)

        #now we OFF generators if they not needed
        #99 + 2 + 1 but consumes 100 -> off second
        for gen in online:
            if (gen_out - gen.get_output()[h]) >= consump_in:
                gen_id.remove(gen.get_id())
                gen_out -= gen.get_output()[h]
            
    
    return gen_shedule, con_scedule



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("generators_data", help="Path to the CSV generators")
    parser.add_argument("test_data", help="Path to the CSV test_data")
    args = parser.parse_args()
    
    generators_list = []
    consumers_list = []

    with open(args.generators_data, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = Generator(row['gen_id'], row['type'], float(row['cost_per_kwh']), [float(row[f"h{i}"]) for i in range(24)])
            generators_list.append(tmp)
    
    with open(args.test_data, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            consumers_list.append([row['consumer_id'], [float(row[f"h{i}"]) for i in range(24)]])




    gen_schedule, con_scedule = gens_and_cons(generators_list, consumers_list)

    print(f'{"h":<4} | {"working generators id":^25} | {"cost":^6} | {"consumers_with_no_elec":^20} ' )
    for h in range(24):
        gen_cost = sum(x.get_consume() for x in generators_list if x.get_id() in gen_schedule[h])
        consumers_with_no_elec = sorted([x[0] for x in consumers_list if x[0] not in con_scedule[h]], key= lambda x: int(x))
        print(f'{h:<4} | {" ".join(sorted(gen_schedule[h])):^25} | {gen_cost:^6} | {" ".join(consumers_with_no_elec):<20}')



if __name__ == "__main__":
    main()