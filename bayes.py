#!/usr/bin/python
"""
Bayesian network to solve diagnosis problem. Please see PDF for more info.
"""

import sys
import copy

SYMPTOM_PRESENT = 'T'
SYMPTOM_NOT_PRESENT = 'F'
SYMPTOM_UNKNOWN = 'U'

class Disease(object):
    """
    Represents the diseases.

    Attributes:
    name             : a string for disease's name
    findings         : a list of strings to hold symptoms
    present_probs    : a list of doubles
    probability      : a double for priori prob, ie, P(D)
    not_present_probs: a list of doubles

    present_probs[i] and not_present_probs[i] corresponds to findings[i]
    present_probs holds the probabilities if disease is present
    """

    def __init__(self, name, probability):
        """ constructor """
        self.name = name
        self.probability = probability
        self.findings = []
        self.present_probs = []
        self.not_present_probs = []

    def add_finding(self, finding):
        """ add a symptom """
        self.findings.append(finding)

    def add_present_prob(self, probability):
        """ add a new probability """
        self.present_probs.append(probability)

    def add_not_present_prob(self, probability):
        """ add a new probability """
        self.not_present_probs.append(probability)

    def __str__(self):
        """ string representation """
        info = "Disease: " +  self.name + ", P(D): " + str(self.probability)
        info += "\n" + str(self.findings)
        info += "\n" + str(self.present_probs)
        info += "\n" + str(self.not_present_probs)
        return info


class Patient(object):
    """
    Represents the patients.

    Attributes:
    symptoms : patient.symptoms['<diseasename>']
    max_probs: holds max probability for a disease
    min_probs: holds min probability for a disease
    """

    # name is just a number
    def __init__(self, name):
        self.symptoms = {}
        self.name = name
        self.max_probs = {}
        self.min_probs = {}

    def add_symptom(self, disease, results):
        """ adds a new disease """
        self.symptoms[disease] = results

    def set_max_prob(self, disease, probability):
        """ set max probability for given disease """
        self.max_probs[disease] = probability

    def set_min_prob(self, disease, probability):
        """ set min probability for given disease """
        self.min_probs[disease] = probability

    def __str__(self):
        """ string repres """
        info = "Patient #%s:" % self.name
        for disease, findings in self.symptoms.items():
            info += "\n"
            info += "Disease: " + str(disease.name) + " -> " + str(findings)
        return info

def calculate_probability(disease, symptoms):
    """ calculate probability of disease with given symptoms """
    nominator = disease.probability
    denominator = 0.0
    right = 1.0 - disease.probability
    for i in range(len(symptoms)):
        if symptoms[i] == SYMPTOM_PRESENT:
            nominator *= disease.present_probs[i]
            right *= disease.not_present_probs[i]
        elif symptoms[i] == SYMPTOM_NOT_PRESENT:
            nominator *= (1.0 - disease.present_probs[i])
            right *= (1.0 - disease.not_present_probs[i])
    denominator = right + nominator
    return round(nominator / denominator, 4)

def generate_all_symptoms(symptoms):
    """ fill unknown test results and return all possibilities """
    result = []
    generate_helper(result, symptoms, 0)
    return result #result is a list of lists

def generate_helper(result_list, symptoms, start):
    """ recursively fill all unknown symptoms """
    if start >= len(symptoms):
        # [TODO] it might be better to the calculation right here
        # if test cases are big, memory might be a probleb ^^
        result_list.append(symptoms)

    for i in range(start, len(symptoms)):
        if symptoms[i] == SYMPTOM_UNKNOWN:
            new_list = copy.deepcopy(symptoms)
            new_list2 = copy.deepcopy(symptoms)
            new_list[i] = SYMPTOM_PRESENT
            new_list2[i] = SYMPTOM_NOT_PRESENT

            generate_helper(result_list, new_list, i+1)
            generate_helper(result_list, new_list2, i+1)
            return

    result_list.append(symptoms)

def question_1(patient):
    """ returns answer for question 1 for given patient """
    result = {}
    for disease, symptoms in patient.symptoms.iteritems():
        prob = calculate_probability(disease, symptoms)
        result[disease.name] = "%.4f" % prob
    return result

def question_2(patient):
    """ returns answer for question 2 for given patient """
    result = {}
    for disease, symptoms in patient.symptoms.iteritems():
        symptoms_list = generate_all_symptoms(symptoms)
        if not symptoms_list: # there are no unknowns
            symptoms_list = [symptoms]
        max_prob = 0.0
        min_prob = 1.0
        for sym_list in symptoms_list:
            prob = calculate_probability(disease, sym_list)
            if prob > max_prob:
                max_prob = prob
            if prob < min_prob:
                min_prob = prob
        min_str = "%.4f" % min_prob
        max_str = "%.4f" % max_prob
        result[disease.name] = [min_str, max_str]
        patient.set_max_prob(disease, max_prob)
        patient.set_min_prob(disease, min_prob)
    return result

def question_3(patient):
    """ returns answer for question 3 for given patient """
    result = {}
    for disease, symptoms in patient.symptoms.iteritems():
        current_probability = calculate_probability(disease, symptoms)
        max_list = [current_probability, -1, 'N', "{"]
        min_list = [current_probability, -1, 'N', "{"]
        for i in range(len(symptoms)):
            if symptoms[i] == SYMPTOM_UNKNOWN:
                temp_list = copy.deepcopy(symptoms)
                # try 'T' first
                temp_list[i] = 'T'
                max_list, min_list = question3_helper(temp_list, max_list, min_list, disease, i)

                # try 'F' now
                temp_list[i] = 'F'
                max_list, min_list = question3_helper(temp_list, max_list, min_list, disease, i)

        if max_list[1] == -1:
            result_max_list = ['none', 'N']
        else:
            result_max_list = [disease.findings[max_list[1]], max_list[2]]

        if min_list[1] == -1:
            result_min_list = ['none', 'N']
        else:
            result_min_list = [disease.findings[min_list[1]], min_list[2]]

        result_list = [result_max_list[0], result_max_list[1]]
        result_list += [result_min_list[0], result_min_list[1]]

        result[disease.name] = result_list
    return result

def question3_helper(symptoms, max_list, min_list, disease, i):
    prob = calculate_probability(disease, symptoms)
    if prob > max_list[0]:
        max_list = [prob, i, symptoms[i], disease.findings[i]]
    elif prob == max_list[0]:
        if disease.findings[i].lower() < max_list[3].lower():
            max_list = [prob, i, symptoms[i], disease.findings[i]]

    if prob < min_list[0]:
        min_list = [prob, i, symptoms[i], disease.findings[i]]
    elif prob == min_list[0]:
        if disease.findings[i].lower() < min_list[3].lower():
            min_list = [prob, i, symptoms[i], disease.findings[i]]

    return max_list, min_list

def get_disease(input_file):
    """ return a disease object from following 4 lines in the file """
    line = input_file.readline()
    line_split = line.split()
    name = line_split[0]
    prob = float(line_split[2])
    disease = Disease(name, prob)
    line = input_file.readline()
    symptomps = eval(line)
    line = input_file.readline()
    present_probs = eval(line)
    line = input_file.readline()
    not_present_probs = eval(line)

    disease.findings = symptomps
    for prob in present_probs:
        disease.add_present_prob(float(prob))
    for prob in not_present_probs:
        disease.add_not_present_prob(float(prob))

    return disease

def main():
    """ driving method """
    if len(sys.argv) != 3 or sys.argv[1] != "-i":
        print "usage: %s -i inputfile" % sys.argv[0]
        return

    if len(sys.argv[2]) < 5 or sys.argv[2][-4:] != ".txt":
        print "input file name should be in form *.txt"
        return

    tokens = sys.argv[2].split("/")
    token = tokens[-1]
    tokens = token.split(".")
    # assumes at this point we have filename.txt
    output_name = tokens[0] + "_inference." + tokens[1]

    diseases = []
    patients = []

    with open(sys.argv[2]) as input_file:
        line = input_file.readline()
        line_split = line.split()
        num_diseases = int(line_split[0])
        num_patients = int(line_split[1])
        for _ in range(0, num_diseases):
            disease = get_disease(input_file)
            diseases.append(disease)
        for i in range(0, num_patients):
            patient = Patient(str(i))
            for j in range(0, num_diseases):
                line = input_file.readline()
                patient.add_symptom(diseases[j], eval(line))
            patients.append(patient)

    with open(output_name, 'w') as out:
        i = 1
        for patient in patients:
            """
            print "Patient-%d" % (i+1)
            print str(question_1(patient))
            print str(question_2(patient))
            print str(question_3(patient))
            """
            out.write("Patient-%d:\n" % (i))
            out.write(str(question_1(patient)) + "\n")
            out.write(str(question_2(patient)) + "\n")
            out.write(str(question_3(patient)) + "\n")
            i += 1


if __name__ == "__main__":
    main()
