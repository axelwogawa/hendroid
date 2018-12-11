import pifacedigitalio as pfdio

pfd = pfdio.PiFaceDigital()

#inputs
btn_op = pfd.input_pins[0].value  #the open button
btn_cl = pfd.input_pins[3].value  #the close button
sns_op = pfd.input_pins[4].value  #the open position sensor
sns_cl = pfd.input_pins[5].value  #the closed position sensor

#outputs
rel_op = pfd.output_pins[0].value  #the open motor relay
rel_cl = pfd.output_pins[1].value  #the close motor relay
rel_ro = pfd.output_pins[2].value  #the room light relay
lgt_op = pfd.output_pins[3].value  #the led of the open button
lgt_cl = pfd.output_pins[4].value  #the led of the close button

m_s0 = 0
m_s3 = 0
m_motor_op = False
m_motor_down = False

while True:
    s0 = pfd.switches[0].value
    s12 = pfd.switches[1].value or pfd.switches[2].value
    s3 = pfd.switches[3].value
    
    if m_s0 == 0 and s0 == 1:
        rel_motor_op.value = not m_motor_op
        rel_motor_down.value = 0
        m_motor_op = not m_motor_op
        m_motor_down = False
    if m_s3 == 0 and s3 == 1:
        rel_motor_down.value = not m_motor_down
        rel_motor_op.value = 0
        m_motor_down = not m_motor_down
        m_motor_op = False
    if s12:
        rel_motor_op.value = 0
        rel_motor_down.value = 0
        m_motor_op = False
        m_motor_down = False
        if s0 and s3:
            break
        
    m_s0 = s0
    m_s3 = s3
        
